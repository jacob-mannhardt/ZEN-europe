"""Generating datasets with the ZEN-europe CLI, one model at a time.

Each model is generated in its own process with the same command a user would
run, so the dashboard does not change how ZEN-europe creates a dataset::

    python -m zen_europe --model <name> --models_path <workspace>/models.yaml
        --config_path <config> --output_path <workspace>/created_models

The jobs run one after another. Generating several models at once is what
``zen-europe --all`` does, but models that reload a cache must not run at
the same time, and a queue keeps the logs apart.
"""

import json
import os
import queue
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

from . import models_file, reference, structure
from .paths import (
    CONFIG_PATH,
    LOG_PATH,
    META_PATH,
    MODELS_PATH,
    OUTPUT_PATH,
    ZEN_EUROPE_ROOT,
)


@dataclass
class Job:
    id: str
    model: str
    status: str = "queued"  # queued, running, done, failed, cancelled
    created: float = field(default_factory=time.time)
    started: float | None = None
    finished: float | None = None
    returncode: int | None = None
    command: list[str] = field(default_factory=list)
    settings_patch: dict[str, Any] = field(default_factory=dict)
    # "model" for a model of the models file, "reference" for the defaults
    kind: str = "model"
    fingerprint: dict[str, Any] = field(default_factory=dict)

    @property
    def log_path(self):
        return LOG_PATH / f"{self.id}.log"


class JobQueue:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._worker = threading.Thread(target=self._run_forever, daemon=True)
        self._worker.start()

    def submit(self, model: str) -> Job:
        """Queue the generation of a model of the saved models file."""
        # fails early for a model that is not saved. The patch is recorded now,
        # since the models file may be edited while the job waits.
        patch = models_file.settings_patch(model)
        problem = structure.check(patch)
        if problem:
            raise ValueError(f"Model '{model}' cannot be generated: {problem}")
        job = Job(id=uuid.uuid4().hex[:12], model=model, settings_patch=patch)
        job.command = [
            sys.executable,
            "-m",
            "zen_europe",
            "--model",
            model,
            "--models_path",
            str(MODELS_PATH),
            "--config_path",
            str(CONFIG_PATH),
            "--output_path",
            str(OUTPUT_PATH),
        ]
        return self._enqueue(job)

    def submit_reference(self) -> Job:
        """Queue the generation of the dataset of the default settings."""
        job = Job(
            id=uuid.uuid4().hex[:12],
            model=reference.LABEL,
            kind="reference",
            command=reference.command(),
            fingerprint=reference.fingerprint(),
        )
        return self._enqueue(job)

    def ensure_reference(self) -> Job | None:
        """Queue the defaults if they are missing or outdated and not queued yet."""
        if self.reference_job() is not None:
            return None
        state = reference.status()
        if state["exists"] and not state["outdated"]:
            return None
        return self.submit_reference()

    def reference_job(self) -> Job | None:
        """The queued or running generation of the defaults, if any."""
        with self._lock:
            return next(
                (
                    job
                    for job in self._jobs.values()
                    if job.kind == "reference" and job.status in ("queued", "running")
                ),
                None,
            )

    def _enqueue(self, job: Job) -> Job:
        with self._lock:
            self._jobs[job.id] = job
        self._queue.put(job.id)
        return job

    def cancel(self, job_id: str) -> Job:
        job = self._jobs[job_id]
        with self._lock:
            if job.status == "queued":
                job.status = "cancelled"
                job.finished = time.time()
            elif job.status == "running" and self._process is not None:
                job.status = "cancelled"
                self._process.kill()
        return job

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            jobs = sorted(
                self._jobs.values(), key=lambda job: job.created, reverse=True
            )
            return [self._to_dict(job) for job in jobs]

    def get(self, job_id: str) -> Job:
        return self._jobs[job_id]

    def log(self, job_id: str, offset: int = 0) -> dict[str, Any]:
        """The log of a job from a byte offset, so it can be followed."""
        job = self._jobs[job_id]
        text, size = "", offset
        if job.log_path.exists():
            with open(job.log_path, "rb") as f:
                f.seek(offset)
                data = f.read()
            text = data.decode("utf-8", errors="replace")
            size = offset + len(data)
        return {"job": self._to_dict(job), "text": text, "offset": size}

    @staticmethod
    def _to_dict(job: Job) -> dict[str, Any]:
        data = asdict(job)
        data.pop("command")
        data.pop("fingerprint")
        return data

    def _run_forever(self) -> None:
        while True:
            job_id = self._queue.get()
            job = self._jobs[job_id]
            if job.status != "queued":
                continue
            try:
                self._run(job)
            except Exception as error:  # report, keep the worker alive
                job.status = "failed"
                job.finished = time.time()
                with open(job.log_path, "a", encoding="utf-8") as log:
                    log.write(f"\nThe dashboard could not run the job: {error}\n")

    def _run(self, job: Job) -> None:
        LOG_PATH.mkdir(parents=True, exist_ok=True)
        env = {**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"}

        with open(job.log_path, "w", encoding="utf-8") as log:
            log.write("$ " + " ".join(job.command) + "\n\n")
            log.flush()
            with self._lock:
                job.status = "running"
                job.started = time.time()
                self._process = subprocess.Popen(
                    job.command,
                    cwd=ZEN_EUROPE_ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env=env,
                )
            returncode = self._process.wait()

        with self._lock:
            self._process = None
            job.returncode = returncode
            job.finished = time.time()
            if job.status != "cancelled":
                job.status = "done" if returncode == 0 else "failed"

        if job.status == "done" and job.kind == "reference":
            reference.record(job.finished, job.fingerprint)
        elif job.status == "done":
            META_PATH.mkdir(parents=True, exist_ok=True)
            meta = {
                "model": job.model,
                "generated": job.finished,
                "duration": job.finished - (job.started or job.finished),
                "settings_patch": job.settings_patch,
                "job": job.id,
            }
            (META_PATH / f"{job.model}.json").write_text(
                json.dumps(meta, indent=2), encoding="utf-8"
            )


jobs = JobQueue()
