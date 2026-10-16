"""The sectors, technologies and carriers of a model, before it is generated.

This is what the model structure pages of the ZEN-europe documentation show,
computed with ZEN-creator's ``model_structure`` for the settings of one
model. Only the carrier attributes are built, so no raw data is read and a
structure takes a fraction of a second.
"""

import threading
from functools import lru_cache
from typing import Any

from zen_creator import Model, model_structure
from zen_creator.utils.config import Config
from zen_creator.utils.settings import Settings

from .paths import CONFIG_PATH, ZEN_EUROPE_ROOT

# building a model touches the class-level registries of ZEN-creator
_lock = threading.Lock()


def _config() -> Config:
    config = Config.load_from_yaml(CONFIG_PATH)
    # the configuration resolves source_path relative to the folder ZEN-europe
    # is run from, which is the repository root
    if config.source_path is not None:
        config.source_path = str((ZEN_EUROPE_ROOT / config.source_path).resolve())
    return config


def structure(patch: dict[str, Any] | None) -> dict[str, Any]:
    """The structure of the model with the given settings patch.

    The result also lists the elements that the patch adds or removes
    compared to the configuration file without any patch.

    Raises:
        ValueError: If the settings are invalid, or the sectors are
            inconsistent, e.g. a sector misses a sector it requires.
    """
    with _lock:
        result = _structure(patch or {})
        base = _base_structure()

    elements = set(result["technologies"]) | set(result["carriers"])
    base_elements = set(base["technologies"]) | set(base["carriers"])
    result["compared_to_base"] = {
        "added": sorted(elements - base_elements, key=str.lower),
        "removed": sorted(base_elements - elements, key=str.lower),
    }
    return result


def check(patch: dict[str, Any] | None) -> str | None:
    """Why the model with the given patch cannot be generated, if it cannot.

    Checks what ZEN-creator checks before writing, which otherwise only fails
    after all data has been read: the sectors are consistent and every
    carrier a technology uses is part of the model.
    """
    try:
        with _lock:
            result = _structure(patch or {})
    except Exception as error:
        if isinstance(error, KeyError):
            return f"Unknown element {error}. It may already be removed by a sector."
        return str(error)
    missing = result["missing_carriers"]
    if missing:
        listing = "; ".join(
            f"{carrier} (used by {', '.join(techs)})"
            for carrier, techs in missing.items()
        )
        return (
            f"Technologies use carriers that are not part of the model: {listing}. "
            "Remove these technologies too, or keep the carriers."
        )
    return None


def _structure(patch: dict[str, Any]) -> dict[str, Any]:
    settings = Settings.load_from_yaml(CONFIG_PATH, patch=patch)
    model = Model.from_config(_config(), settings=settings)
    result = model_structure(model)
    result["carrier_flows"] = [list(flow) for flow in result["carrier_flows"]]
    result["nodes"] = list(settings.region.set_nodes)
    result["missing_carriers"] = _missing_carriers(result)
    return result


def _missing_carriers(result: dict[str, Any]) -> dict[str, list[str]]:
    """The carriers technologies use that are not in the model, and their users."""
    missing: dict[str, list[str]] = {}
    for name, tech in result["technologies"].items():
        used = set(tech.get("reference_carrier", []))
        used |= set(tech.get("input_carrier", [])) | set(tech.get("output_carrier", []))
        for carrier in sorted(used - set(result["carriers"])):
            missing.setdefault(carrier, []).append(name)
    return missing


@lru_cache(maxsize=1)
def _base_structure() -> dict[str, Any]:
    return _structure({})
