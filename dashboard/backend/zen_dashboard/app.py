"""The HTTP API of the dashboard, and the built frontend."""

from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import catalog, datasets, models_file, reference, structure
from .jobs import jobs
from .paths import (
    CONFIG_PATH,
    FRONTEND_DIST,
    MODELS_PATH,
    OUTPUT_PATH,
    ZEN_EUROPE_ROOT,
    ensure_workspace,
)

ensure_workspace()

app = FastAPI(title="ZEN-europe dashboard")


class ModelsDoc(BaseModel):
    defaults: dict[str, Any] = {}
    models: dict[str, dict[str, Any]]


class StructureRequest(BaseModel):
    patch: dict[str, Any] = {}


class GenerateRequest(BaseModel):
    models: list[str]


# ---------- settings and models ----------


@app.get("/api/info")
def info() -> dict[str, Any]:
    return {
        "zen_europe_root": str(ZEN_EUROPE_ROOT),
        "config_path": str(CONFIG_PATH),
        "models_path": str(MODELS_PATH),
        "output_path": str(OUTPUT_PATH),
    }


@app.get("/api/catalog")
def get_catalog() -> dict[str, Any]:
    return catalog.catalog()


@app.get("/api/models")
def get_models() -> dict[str, Any]:
    return models_file.load()


@app.post("/api/models/validate")
def validate_models(doc: ModelsDoc) -> dict[str, Any]:
    return models_file.validate(doc.model_dump())


@app.put("/api/models")
def save_models(doc: ModelsDoc) -> dict[str, Any]:
    return models_file.save(doc.model_dump())


@app.post("/api/structure")
def get_structure(request: StructureRequest) -> dict[str, Any]:
    try:
        return structure.structure(request.patch)
    except Exception as error:  # an invalid configuration is shown to the user
        raise HTTPException(status_code=400, detail=_message(error)) from error


# ---------- generation ----------


@app.post("/api/jobs")
def submit_jobs(request: GenerateRequest) -> list[dict[str, Any]]:
    submitted = []
    for model in request.models:
        try:
            job = jobs.submit(model)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=_message(error)) from error
        submitted.append(jobs.log(job.id)["job"])
    # the defaults are generated after the models, so that the changes of
    # the models can be highlighted
    reference_job = jobs.ensure_reference()
    if reference_job is not None:
        submitted.append(jobs.log(reference_job.id)["job"])
    return submitted


@app.get("/api/reference")
def reference_status() -> dict[str, Any]:
    """Whether the dataset of the defaults exists, is outdated or is generated."""
    job = jobs.reference_job()
    return {**reference.status(), "job": jobs.log(job.id)["job"] if job else None}


@app.post("/api/reference")
def generate_reference() -> dict[str, Any]:
    """Generate the dataset of the defaults (again)."""
    job = jobs.reference_job() or jobs.submit_reference()
    return jobs.log(job.id)["job"]


@app.get("/api/jobs")
def list_jobs() -> list[dict[str, Any]]:
    return jobs.list()


@app.get("/api/jobs/{job_id}/log")
def job_log(job_id: str, offset: int = 0) -> dict[str, Any]:
    try:
        return jobs.log(job_id, offset)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Unknown job '{job_id}'."
        ) from None


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str) -> dict[str, Any]:
    try:
        jobs.cancel(job_id)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Unknown job '{job_id}'."
        ) from None
    return jobs.log(job_id)["job"]


# ---------- datasets ----------


@app.get("/api/datasets")
def list_datasets() -> list[dict[str, Any]]:
    return datasets.list_datasets()


@app.get("/api/datasets/{name}")
def dataset_overview(name: str) -> dict[str, Any]:
    return datasets.overview(name)


@app.delete("/api/datasets/{name}")
def delete_dataset(name: str) -> dict[str, Any]:
    datasets.delete(name)
    return {"deleted": name}


@app.get("/api/datasets/{name}/download")
def download_dataset(name: str, background: BackgroundTasks) -> FileResponse:
    path = datasets.zip_dataset(name)
    background.add_task(path.unlink, missing_ok=True)
    return FileResponse(path, filename=f"{name}.zip", media_type="application/zip")


@app.get("/api/datasets/{name}/compare")
def compare_dataset(name: str, reference: str | None = None) -> dict[str, Any]:
    """What differs from a reference dataset, by default one without changes."""
    other = reference or datasets.default_reference(name)
    if other is None:
        return {
            "reference": None,
            "reference_label": None,
            "elements": {},
            "removed": [],
        }
    return datasets.compare(name, other)


@app.get("/api/datasets/{name}/elements/{element_type}/{element}")
def element_details(name: str, element_type: str, element: str) -> dict[str, Any]:
    return datasets.element_details(name, element_type, element)


@app.get("/api/datasets/{name}/elements/{element_type}/{element}/yearly/{attribute}")
def element_yearly_values(
    name: str, element_type: str, element: str, attribute: str
) -> dict[str, Any]:
    """The values of an attribute in every year, with its yearly variation."""
    return datasets.yearly_values(name, element_type, element, attribute)


@app.get("/api/datasets/{name}/elements/{element_type}/{element}/data/{file}")
def element_data(
    name: str, element_type: str, element: str, file: str
) -> dict[str, Any]:
    return datasets.read_data(name, element_type, element, file)


@app.exception_handler(datasets.NotFound)
def _not_found(request: Request, error: Exception) -> JSONResponse:
    """Turn a missing dataset, element or file into a 404."""
    return JSONResponse(status_code=404, content={"detail": str(error)})


def _message(error: Exception) -> str:
    if isinstance(error, KeyError):
        return f"Unknown element {error}. It may already be removed by a sector."
    return str(error)


# ---------- frontend ----------

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
