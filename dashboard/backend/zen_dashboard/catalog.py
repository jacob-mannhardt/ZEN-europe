"""The settings that can be varied per model, and the values they accept.

Everything here is read from the registries of ZEN-creator, which ZEN-europe
fills when it is imported: the settings categories, the sectors and the
elements. Adding a setting or an element to ZEN-europe makes it appear in
the dashboard without changes here.
"""

import inspect
import types
import typing
from pathlib import Path
from typing import Any, Literal

from zen_creator.elements import (
    Carrier,
    ConversionTechnology,
    EnergySystem,
    RetrofittingTechnology,
    StorageTechnology,
    TransportTechnology,
)
from zen_creator.elements.element import Element
from zen_creator.sectors import Sector
from zen_creator.utils.settings import Settings, SettingsCategory

from . import descriptions
from .paths import CONFIG_PATH

# categories the dashboard sets itself, so they are not offered per model
HIDDEN_CATEGORIES = {"output"}
# categories that are collapsed by default
ADVANCED_CATEGORIES = {"cache"}

CATEGORY_ORDER = [
    "time",
    "region",
    "structure",
    "investment",
    "emissions",
    "cost",
    "availability",
    "data_source",
    "max_load",
    "scenario",
    "cache",
]

ELEMENT_TYPES = {
    "retrofitting_technology": RetrofittingTechnology,
    "conversion_technology": ConversionTechnology,
    "storage_technology": StorageTechnology,
    "transport_technology": TransportTechnology,
    "carrier": Carrier,
}

# the element type a list setting of the structure category picks from
LIST_OPTIONS = {
    "region.set_nodes": "nodes",
    "structure.set_sectors": "sectors",
    "structure.remove_sectors": "sectors",
    "structure.set_conversion_technologies": "conversion_technology",
    "structure.set_storage_technologies": "storage_technology",
    "structure.set_transport_technologies": "transport_technology",
    "structure.set_retrofitting_technologies": "retrofitting_technology",
    "structure.set_carriers": "carrier",
    "structure.remove_technologies": "elements",
}


def _is_project_class(cls: type) -> bool:
    """Whether a registered class is defined by ZEN-europe, not a ZEN-creator base."""
    return not cls.__module__.startswith("zen_creator")


def element_options() -> dict[str, list[dict[str, str]]]:
    """The registered elements per element type, with their description."""
    options: dict[str, list[dict[str, str]]] = {key: [] for key in ELEMENT_TYPES}
    for name, cls in Element.get_registry().items():
        if not _is_project_class(cls):
            continue
        element_type = next(
            (key for key, base in ELEMENT_TYPES.items() if issubclass(cls, base)), None
        )
        if element_type is None:
            continue
        options[element_type].append({"name": name, "description": _short_doc(cls)})
    for entries in options.values():
        entries.sort(key=lambda entry: entry["name"].lower())
    return options


def sector_options() -> list[dict[str, Any]]:
    """The registered sectors with their description and required sectors."""
    return [
        {
            "name": name,
            "description": inspect.getdoc(cls) or "",
            "required_sectors": list(cls.required_sectors),
        }
        for name, cls in sorted(Sector._sector_registry.items())
    ]


def energy_system_options() -> list[str]:
    return sorted(
        name
        for name, cls in EnergySystem.get_registry().items()
        if issubclass(cls, EnergySystem) and _is_project_class(cls)
    )


def _short_doc(cls: type) -> str:
    doc = inspect.getdoc(cls) or ""
    return doc.split("\n\n")[0].replace("\n", " ")


def _field_kind(annotation: Any) -> tuple[str, list[Any] | None]:
    """The input kind of a settings field and, for a choice, its options."""
    origin = typing.get_origin(annotation)
    if origin is Literal:
        return "choice", list(typing.get_args(annotation))
    if origin in (list, tuple):
        return "list", None
    if origin in (typing.Union, types.UnionType):
        args = [arg for arg in typing.get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _field_kind(args[0])
    if annotation is bool:
        return "bool", None
    if annotation is int:
        return "int", None
    if annotation is float:
        return "float", None
    if annotation is str:
        return "str", None
    if annotation is Path:
        return "path", None
    return "json", None


def base_settings() -> dict[str, Any]:
    """The settings of the configuration file, before any model patches them."""
    return Settings.load_from_yaml(CONFIG_PATH).model_dump(mode="json")


def settings_schema() -> dict[str, Any]:
    """Every category and field that a model can patch, with its explanation."""
    registry = {
        name: cls
        for name, cls in SettingsCategory.get_registry().items()
        if cls is not SettingsCategory and name not in HIDDEN_CATEGORIES
    }
    order = [name for name in CATEGORY_ORDER if name in registry]
    order += sorted(set(registry) - set(order))

    categories = []
    for name in order:
        cls = registry[name]
        controls = getattr(cls, "controls", {})
        fields = []
        for field_name, info in cls.model_fields.items():
            kind, choices = _field_kind(info.annotation)
            key = f"{name}.{field_name}"
            description = info.description or descriptions.FIELDS.get(key)
            if description is None and name == "cache":
                description = descriptions.describe_cache_field(field_name)
            fields.append(
                {
                    "name": field_name,
                    "kind": kind,
                    "choices": choices,
                    "options": LIST_OPTIONS.get(key),
                    "default": _jsonable(info.get_default(call_default_factory=True)),
                    "description": _single_line(description or ""),
                    "controls": controls.get(field_name),
                }
            )
        categories.append(
            {
                "name": name,
                "description": descriptions.CATEGORIES.get(name)
                or _single_line(inspect.getdoc(cls) or ""),
                "advanced": name in ADVANCED_CATEGORIES,
                "fields": fields,
            }
        )
    return {"categories": categories}


def _single_line(doc: str) -> str:
    """A docstring as flowing text, keeping its paragraphs apart."""
    paragraphs = inspect.cleandoc(doc).split("\n\n")
    return "\n\n".join(" ".join(p.split()) for p in paragraphs)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    return value


def catalog() -> dict[str, Any]:
    """Everything the settings editor needs: schema, base values and options."""
    base = base_settings()
    elements = element_options()
    return {
        "config_path": str(CONFIG_PATH),
        "schema": settings_schema(),
        "base": base,
        "options": {
            "nodes": base["region"]["set_nodes"],
            "sectors": sector_options(),
            "energy_systems": energy_system_options(),
            "elements": elements,
        },
    }
