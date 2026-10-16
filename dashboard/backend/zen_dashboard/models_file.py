"""The dashboard's models file, which declares the models the user configures.

The file has the format of ZEN-europe's models file (see ZEN-creator's
``ModelSet``), so the generated datasets are reproducible with the CLI::

    zen-europe --all --models_path <workspace>/models.yaml

It lives in the workspace, so editing models never changes ZEN-europe's own
``data/models.yaml``. On first start it is seeded from that file.
"""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml
from zen_creator.utils.settings import ModelSet, Settings

from . import structure
from .paths import CONFIG_PATH, MODELS_PATH, ZEN_EUROPE_MODELS_PATH

# a model name becomes a folder name
MODEL_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")

EMPTY_FILE: dict[str, Any] = {"models": {"base": {}}}


def load() -> dict[str, Any]:
    """Read the models file, seeding it on first use."""
    if not MODELS_PATH.exists():
        MODELS_PATH.parent.mkdir(parents=True, exist_ok=True)
        if ZEN_EUROPE_MODELS_PATH.exists():
            shutil.copyfile(ZEN_EUROPE_MODELS_PATH, MODELS_PATH)
        else:
            _write(EMPTY_FILE, MODELS_PATH)

    with open(MODELS_PATH, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return normalize(raw)


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    """Bring a models file into the shape the frontend edits."""
    defaults = (raw.get("defaults") or {}).get("settings") or {}
    models = {}
    for name, entry in (raw.get("models") or {}).items():
        entry = entry or {}
        models[str(name)] = {
            "extends": entry.get("extends"),
            "settings": entry.get("settings") or {},
        }
    return {"defaults": defaults, "models": models}


def to_yaml_dict(doc: dict[str, Any]) -> dict[str, Any]:
    """The models file as it is written, with empty entries left out."""
    out: dict[str, Any] = {}
    if doc.get("defaults"):
        out["defaults"] = {"settings": doc["defaults"]}
    models: dict[str, Any] = {}
    for name, entry in doc.get("models", {}).items():
        model: dict[str, Any] = {}
        if entry.get("extends"):
            model["extends"] = entry["extends"]
        if entry.get("settings"):
            model["settings"] = entry["settings"]
        models[name] = model
    out["models"] = models
    return out


def validate(doc: dict[str, Any]) -> dict[str, Any]:
    """Validate every model of a models file the way ZEN-europe will.

    Returns:
        A mapping with "file_error" for an error of the whole file, "errors"
        mapping each model with invalid settings to its error message, and
        "problems" mapping each model whose structure cannot be generated
        (e.g. a missing carrier) to the reason. A file with errors is not
        saved; a model with a problem is saved but cannot be generated.
    """
    errors: dict[str, str] = {}
    problems: dict[str, str] = {}
    for name in doc.get("models", {}):
        if not MODEL_NAME.match(name):
            errors[name] = (
                "A model name may only contain letters, digits, '_', '.' and '-', "
                "and must start with a letter or digit."
            )

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "models.yaml"
        _write(to_yaml_dict(doc), path)
        try:
            model_set = ModelSet.load_from_yaml(path)
        except ValueError as error:
            return {
                "file_error": _clean(str(error), path),
                "errors": errors,
                "problems": problems,
            }

        for name in model_set.names:
            patch = model_set.settings_patch(name)
            try:
                Settings.load_from_yaml(CONFIG_PATH, patch=patch)
            except ValueError as error:
                errors.setdefault(name, _clean(str(error), path))
                continue
            problem = structure.check(patch)
            if problem:
                problems[name] = problem

    return {"file_error": None, "errors": errors, "problems": problems}


def save(doc: dict[str, Any]) -> dict[str, Any]:
    """Validate and write the models file. Nothing is written if it is invalid."""
    result = validate(doc)
    if result["file_error"] is None and not result["errors"]:
        _write(to_yaml_dict(doc), MODELS_PATH)
        result["saved"] = True
    else:
        result["saved"] = False
    return result


def settings_patch(name: str) -> dict[str, Any]:
    """The settings patch of a saved model."""
    return ModelSet.load_from_yaml(MODELS_PATH).settings_patch(name)


def _write(data: dict[str, Any], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def _clean(message: str, temp_path: Path) -> str:
    """Hide the path of the temporary file that was validated."""
    return message.replace(str(temp_path), "models.yaml")
