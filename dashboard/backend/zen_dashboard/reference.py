"""The dataset of ZEN-europe's default settings, to show what a model changes.

The data explorer highlights what differs in a dataset from the defaults. To
know the default values, the dashboard generates the dataset of the
configuration file without any model patch once, with the plain CLI::

    python -m zen_europe --name defaults --config_path <config>
        --output_path <workspace>/reference

It is kept apart from the generated models, and is generated again when it
is outdated: when the configuration file, ZEN-europe's commit or the version
of ZEN-europe or ZEN-creator differ from those it was generated with.
"""

import hashlib
import json
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .paths import CONFIG_PATH, REFERENCE_PATH, ZEN_EUROPE_ROOT

NAME = "defaults"
# how the reference is named where a dataset name is expected
KEY = "__defaults__"
LABEL = "ZEN-europe defaults"

META_FILE = REFERENCE_PATH / "meta.json"


def dataset_path() -> Path:
    return REFERENCE_PATH / NAME


def command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "zen_europe",
        "--name",
        NAME,
        "--config_path",
        str(CONFIG_PATH),
        "--output_path",
        str(REFERENCE_PATH),
    ]


def fingerprint() -> dict[str, Any]:
    """What the default dataset depends on, apart from the raw data."""
    return {
        "config": hashlib.sha1(CONFIG_PATH.read_bytes()).hexdigest(),
        "commit": _commit(),
        "zen_europe": _version("zen_europe"),
        "zen_creator": _version("zen-creator"),
    }


def status() -> dict[str, Any]:
    """Whether the reference exists, when it was generated and if it is outdated."""
    exists = (dataset_path() / "system.yaml").exists()
    meta: dict[str, Any] = {}
    if META_FILE.exists():
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    return {
        "exists": exists,
        "generated": meta.get("generated"),
        "outdated": exists and meta.get("fingerprint") != fingerprint(),
    }


def record(generated: float, recorded: dict[str, Any]) -> None:
    """Record what a newly generated reference was generated with."""
    META_FILE.write_text(
        json.dumps({"generated": generated, "fingerprint": recorded}, indent=2),
        encoding="utf-8",
    )


def _commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ZEN_EUROPE_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    return result.stdout.strip() or None


def _version(package: str) -> str | None:
    try:
        return version(package)
    except PackageNotFoundError:
        return None
