"""Reading generated datasets: their elements, attributes, data files and sources.

A dataset is read from the files ZEN-europe wrote, in the input format of
ZEN-garden::

    <dataset>/system.yaml
    <dataset>/energy_system/attributes.yaml, set_nodes.csv, set_edges.csv, ...
    <dataset>/set_carriers/<carrier>/attributes.yaml, <attribute>*.csv, sources.md
    <dataset>/set_technologies/set_<type>_technologies/<technology>/...
"""

import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from . import reference
from .paths import META_PATH, OUTPUT_PATH

ELEMENT_FOLDERS = {
    "carrier": Path("set_carriers"),
    "conversion_technology": Path("set_technologies") / "set_conversion_technologies",
    "retrofitting_technology": Path("set_technologies")
    / "set_retrofitting_technologies",
    "storage_technology": Path("set_technologies") / "set_storage_technologies",
    "transport_technology": Path("set_technologies") / "set_transport_technologies",
}
ENERGY_SYSTEM = "energy_system"

# the index columns ZEN-garden knows, in the order they are used as the x axis
X_DIMS = ["time", "year", "year_construction"]
SPATIAL_DIMS = ["node", "location", "edge"]
INDEX_DIMS = set(X_DIMS) | set(SPATIAL_DIMS) | {"carrier", "technology"}

MAX_SERIES = 2000


class NotFound(Exception):
    pass


# ---------- datasets ----------


def list_datasets() -> list[dict[str, Any]]:
    """The generated datasets in the workspace, newest first."""
    if not OUTPUT_PATH.exists():
        return []
    datasets = []
    for path in OUTPUT_PATH.iterdir():
        if not (path / "system.yaml").exists():
            continue
        meta = _meta(path.name)
        datasets.append(
            {
                "name": path.name,
                "modified": path.stat().st_mtime,
                "generated": meta.get("generated"),
                "duration": meta.get("duration"),
                "settings_patch": meta.get("settings_patch"),
                "size": _folder_size(path),
            }
        )
    return sorted(datasets, key=lambda d: d["modified"], reverse=True)


def dataset_path(name: str) -> Path:
    path = _inside(OUTPUT_PATH, name)
    if not (path / "system.yaml").exists():
        raise NotFound(f"Dataset '{name}' does not exist.")
    return path


def overview(name: str) -> dict[str, Any]:
    """The system file, nodes, edges and elements of a dataset."""
    path = dataset_path(name)
    system = _read_yaml(path / "system.yaml")
    elements: dict[str, list[str]] = {}
    for element_type, folder in ELEMENT_FOLDERS.items():
        folder_path = path / folder
        elements[element_type] = (
            sorted((p.name for p in folder_path.iterdir() if p.is_dir()), key=str.lower)
            if folder_path.exists()
            else []
        )
    return {
        "name": name,
        "system": system,
        "nodes": _nodes(path),
        "edges": _edges(path),
        "elements": elements,
        "scenarios": (
            _read_yaml(path / "scenarios.yaml")
            if (path / "scenarios.yaml").exists()
            else None
        ),
        "meta": _meta(name),
    }


def delete(name: str) -> None:
    shutil.rmtree(dataset_path(name))
    meta = META_PATH / f"{name}.json"
    if meta.exists():
        meta.unlink()


def zip_dataset(name: str) -> Path:
    """Zip a dataset together with a ZEN-garden config.yaml that runs it.

    The zip unpacks to a folder that ZEN-garden can be run from directly::

        config.yaml
        <name>/system.yaml, energy_system/, set_carriers/, ...
    """
    path = dataset_path(name)
    config = (
        _read_yaml(OUTPUT_PATH / "config.yaml")
        if (OUTPUT_PATH / "config.yaml").exists()
        else {}
    )
    config.setdefault("analysis", {})["dataset"] = name

    fd, zip_name = tempfile.mkstemp(suffix=".zip")
    os.close(fd)
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("config.yaml", yaml.safe_dump(config, sort_keys=False))
        for file in sorted(path.rglob("*")):
            if file.is_file():
                archive.write(file, Path(name) / file.relative_to(path))
    return Path(zip_name)


# ---------- elements ----------


def element_path(name: str, element_type: str, element: str) -> Path:
    root = dataset_path(name)
    if element_type == ENERGY_SYSTEM:
        return root / ENERGY_SYSTEM
    if element_type not in ELEMENT_FOLDERS:
        raise NotFound(f"Unknown element type '{element_type}'.")
    path = _inside(root / ELEMENT_FOLDERS[element_type], element)
    if not path.is_dir():
        raise NotFound(f"Element '{element}' does not exist in dataset '{name}'.")
    return path


def element_details(name: str, element_type: str, element: str) -> dict[str, Any]:
    """The attributes of an element, with their data files and sources."""
    path = element_path(name, element_type, element)
    attributes = (
        _read_yaml(path / "attributes.yaml")
        if (path / "attributes.yaml").exists()
        else {}
    )
    sources = _sources(path / "sources.md")

    data_files = sorted(p.stem for p in path.glob("*.csv"))
    files_of: dict[str, list[str]] = {attr: [] for attr in attributes}
    unassigned = []
    for stem in data_files:
        owner = _owning_attribute(stem, attributes)
        if owner is None:
            unassigned.append(stem)
        else:
            files_of[owner].append(stem)

    rows = []
    for attr, value in attributes.items():
        default, unit, extra = _default(value)
        rows.append(
            {
                "name": attr,
                "default_value": default,
                "unit": unit,
                "extra": extra,
                "files": files_of.get(attr, []),
                "has_sources": attr in sources,
            }
        )
    # files without an attribute entry, e.g. set_nodes of the energy system
    for stem in unassigned:
        rows.append(
            {
                "name": stem,
                "default_value": None,
                "unit": None,
                "extra": None,
                "files": [stem],
                "has_sources": stem in sources,
            }
        )

    return {
        "name": element,
        "type": element_type,
        "attributes": rows,
        "sources": sources,
        "other_files": sorted(
            p.name for p in path.iterdir() if p.suffix not in (".csv",) and p.is_file()
        ),
    }


def _owning_attribute(stem: str, attributes: dict[str, Any]) -> str | None:
    """The attribute a data file belongs to.

    ZEN-creator writes the files of an attribute as ``<attr>``,
    ``<attr>_yearly_variation``, ``<attr>_<year>``, and for a scenario
    ``<attr>_<suffix>`` or ``<attr>_yearly_variation_<suffix>``. The name
    alone can be ambiguous: ``availability_import_yearly_variation`` is the
    yearly variation of ``availability_import``, not a scenario of
    ``availability_import_yearly``. So the attribute whose remainder fits
    the known patterns best is chosen.
    """

    def rank(attr: str) -> tuple[int, int]:
        rest = stem[len(attr) + 1 :]
        if stem == attr:
            fit = 0
        elif rest == "yearly_variation" or rest.startswith("yearly_variation_"):
            fit = 1
        elif rest.isdigit():
            fit = 2
        else:
            fit = 3  # a scenario suffix
        return fit, -len(attr)

    matches = [
        attr for attr in attributes if stem == attr or stem.startswith(attr + "_")
    ]
    return min(matches, key=rank) if matches else None


def _default(value: Any) -> tuple[Any, str | None, Any]:
    """Split an attributes.yaml entry into default value, unit and the rest."""
    if isinstance(value, dict):
        rest = {k: v for k, v in value.items() if k not in ("default_value", "unit")}
        return value.get("default_value"), value.get("unit"), rest or None
    # e.g. the conversion factors, a list of carrier mappings
    return None, None, value


def _sources(path: Path) -> dict[str, str]:
    """Split sources.md into the markdown of each attribute.

    The file has a title and one section per attribute, each a heading
    underlined with dashes.
    """
    if not path.exists():
        return {}
    lines = _read_text(path).splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        if line and re.fullmatch(r"-{3,}", next_line) and len(next_line) >= len(line):
            current = line.strip()
            sections[current] = []
            continue
        if current is None or re.fullmatch(r"-{3,}", line) and not sections[current]:
            continue
        sections[current].append(line)
    return {name: "\n".join(body).strip() for name, body in sections.items()}


# ---------- comparison ----------


def default_reference(name: str) -> str | None:
    """The dataset to compare a dataset with: one without changed settings.

    That is the dataset of the defaults the dashboard generates (see
    reference.py). Until it exists, a generated dataset without any settings
    patch is used, or, of the datasets generated outside the dashboard, which
    have no recorded patch, the one with the CLI's default name.
    """
    if reference.status()["exists"]:
        return reference.KEY
    candidates = [d for d in list_datasets() if d["name"] != name]
    for dataset in candidates:
        if dataset["settings_patch"] == {}:
            return str(dataset["name"])
    for dataset in candidates:
        if dataset["name"] == "zen-europe" and dataset["settings_patch"] is None:
            return "zen-europe"
    return None


def compare(name: str, other: str) -> dict[str, Any]:
    """What differs in a dataset from a reference dataset.

    Returns:
        A mapping with "elements", which maps "<type>/<element>" to its status
        ("changed" or "added") and its changed attributes, and "removed", the
        elements of the reference that the dataset does not contain.
        Unchanged elements are left out. An attribute is changed when its
        entry in attributes.yaml or one of its data files differs.
    """
    if other == reference.KEY:
        if not reference.status()["exists"]:
            raise NotFound("The defaults have not been generated yet.")
        other_path = reference.dataset_path()
    else:
        other_path = dataset_path(other)
    current = _fingerprint(dataset_path(name))
    base = _fingerprint(other_path)

    elements: dict[str, Any] = {}
    for key, element in current.items():
        if key not in base:
            elements[key] = {"status": "added", "attributes": {}}
            continue
        attributes = _changed_attributes(element, base[key])
        if attributes:
            elements[key] = {"status": "changed", "attributes": attributes}
    return {
        "reference": other,
        "reference_label": reference.LABEL if other == reference.KEY else other,
        "elements": elements,
        "removed": sorted(set(base) - set(current)),
    }


def _changed_attributes(
    element: dict[str, Any], other: dict[str, Any]
) -> dict[str, Any]:
    """The attributes of an element that differ from the reference element."""
    attributes, files = element["attributes"], element["files"]
    ref_attributes, ref_files = other["attributes"], other["files"]

    changed: dict[str, Any] = {}
    for attr in set(attributes) | set(ref_attributes):
        if attributes.get(attr) != ref_attributes.get(attr):
            default, _, _ = _default(attributes.get(attr))
            ref_default, _, _ = _default(ref_attributes.get(attr))
            changed[attr] = {
                "default": [ref_default, default],
                "entry_changed": True,
                "files": {},
            }

    names = set(attributes) | set(ref_attributes)
    for stem in set(files) | set(ref_files):
        if files.get(stem) == ref_files.get(stem):
            continue
        owner = _owning_attribute(stem, {n: None for n in names}) or stem
        status = (
            "added"
            if stem not in ref_files
            else "removed" if stem not in files else "changed"
        )
        entry = changed.setdefault(
            owner, {"default": None, "entry_changed": False, "files": {}}
        )
        entry["files"][stem] = status
    return changed


_hashes: dict[tuple[str, int, int], str] = {}


def _fingerprint(path: Path) -> dict[str, dict[str, Any]]:
    """The attributes and data file hashes of every element of a dataset."""
    folders = {(ENERGY_SYSTEM, ENERGY_SYSTEM): path / ENERGY_SYSTEM}
    for element_type, folder in ELEMENT_FOLDERS.items():
        if (path / folder).exists():
            for element_path in (path / folder).iterdir():
                if element_path.is_dir():
                    folders[(element_type, element_path.name)] = element_path

    result = {}
    for (element_type, element), folder in folders.items():
        attributes_file = folder / "attributes.yaml"
        result[f"{element_type}/{element}"] = {
            "attributes": (
                _read_yaml(attributes_file) if attributes_file.exists() else {}
            ),
            "files": {file.stem: _hash(file) for file in folder.glob("*.csv")},
        }
    return result


def _hash(file: Path) -> str:
    """The content hash of a file, cached until the file changes."""
    stat = file.stat()
    key = (str(file), stat.st_mtime_ns, stat.st_size)
    if key not in _hashes:
        _hashes[key] = hashlib.blake2b(file.read_bytes(), digest_size=16).hexdigest()
    return _hashes[key]


# ---------- data files ----------


def read_data(name: str, element_type: str, element: str, file: str) -> dict[str, Any]:
    """A data file of an element, as series to plot.

    A file is either long, with the index columns and one value column, or
    wide, with one column per node or edge. Both are brought into series
    along the x dimension (time, year or year_construction), one series per
    combination of the other index values, e.g. per node.
    """
    path = _inside(element_path(name, element_type, element), f"{file}.csv")
    if not path.exists():
        raise NotFound(f"File '{file}.csv' does not exist.")
    df = pd.read_csv(path)
    long = _long(name, df, file)
    if long is None:
        # a set file without values, e.g. set_edges, or a file with text values
        return {"kind": "table", "columns": list(df.columns), "rows": _rows(df)}
    frame, index, value_name = long
    return _series(frame, index, file, value_name, rows=len(df))


def yearly_values(
    name: str, element_type: str, element: str, attribute: str
) -> dict[str, Any]:
    """The values of an attribute in every year, with its yearly variation.

    ZEN-garden multiplies the value of an attribute with its yearly
    variation, a factor per year. The value is the attribute's data file
    if it has one, else its default value:

    - without data file: the default value times the factor, per year.
    - with a data file per node or edge: each value times the factor, per
      year and node or edge.
    - with a data file along time: the two cannot be shown as one series, so
      ``{"kind": "separate"}`` is returned and both are shown on their own.
    """
    folder = element_path(name, element_type, element)
    factor_file = folder / f"{attribute}_yearly_variation.csv"
    if not factor_file.exists():
        raise NotFound(f"'{attribute}' has no yearly variation.")
    factor_long = _long(name, pd.read_csv(factor_file), factor_file.stem)
    if factor_long is None:
        raise NotFound(f"The yearly variation of '{attribute}' has no values.")
    factor, factor_index, _ = factor_long

    data_file = folder / f"{attribute}.csv"
    if data_file.exists():
        data_long = _long(name, pd.read_csv(data_file), attribute)
        if data_long is None:
            raise NotFound(f"The data of '{attribute}' has no values.")
        data, data_index, _ = data_long
        if "time" in data_index or "year" in data_index:
            return {"kind": "separate"}
        source = "data"
    else:
        attributes = _read_yaml(folder / "attributes.yaml")
        default, _, _ = _default(attributes.get(attribute))
        try:
            default_value = float(default)
        except (TypeError, ValueError):
            raise NotFound(f"'{attribute}' has no numeric default value.") from None
        # the default applies to every node or edge the factor distinguishes
        data_index = [d for d in factor_index if d in SPATIAL_DIMS]
        data = _all_locations(name, data_index).assign(value=default_value)
        source = "default"

    # every value in every year of the factor; a value without a factor for
    # a year keeps its value, as in ZEN-garden (factor 1)
    years = pd.DataFrame({"year": sorted(factor["year"].unique())})
    grid = data.merge(years, how="cross")
    on = [d for d in factor_index if d in grid.columns]
    merged = grid.merge(factor, on=on, how="left", suffixes=("_data", "_factor"))
    merged["value"] = merged["value_data"] * merged["value_factor"].fillna(1.0)
    index = data_index + ["year"]

    result = _series(
        merged[index + ["value"]], index, attribute, attribute, rows=len(merged)
    )
    result["source"] = source
    return result


def _all_locations(name: str, dims: list[str]) -> pd.DataFrame:
    """Every node or edge of a dataset, as a frame with the given columns."""
    if not dims:
        return pd.DataFrame(index=[0])
    path = dataset_path(name)
    if dims == ["edge"]:
        return pd.DataFrame({"edge": [e["edge"] for e in _edges(path)]})
    if len(dims) == 1:
        return pd.DataFrame({dims[0]: [n["node"] for n in _nodes(path)]})
    raise NotFound(f"Cannot combine a default value with a factor by {dims}.")


def _long(
    name: str, df: pd.DataFrame, file: str
) -> tuple[pd.DataFrame, list[str], str] | None:
    """A data file as one row per index combination with its "value".

    Returns:
        The long frame, its index columns and the name of the value, or None
        if the file has no numeric values.
    """
    index = [c for c in df.columns if c in INDEX_DIMS]
    values = [c for c in df.columns if c not in INDEX_DIMS]
    if not values:
        return None
    if any(not pd.api.types.is_numeric_dtype(df[c]) for c in values):
        return None
    if len(values) == 1:
        return df.rename(columns={values[0]: "value"}), index, values[0]
    column_dim = _column_dim(name, values)
    long = df.melt(id_vars=index, value_vars=values, var_name=column_dim)
    return long, index + [column_dim], file


def _series(
    long: pd.DataFrame, index: list[str], file: str, value_name: str, rows: int
) -> dict[str, Any]:
    """The series of a long frame along its x dimension, one per group."""
    x_dim = next((d for d in X_DIMS if d in index), None)
    # a single value along x, e.g. one construction year, is shown as bars
    x_single = None
    if x_dim is not None and long[x_dim].nunique() == 1:
        x_single = {"dim": x_dim, "value": _plain(long[x_dim].iloc[0])}
        index = [d for d in index if d != x_dim]
        x_dim = None
    spatial_dim = next((d for d in SPATIAL_DIMS + ["column"] if d in index), None)
    group_dims = [d for d in index if d != x_dim]

    if x_dim is not None:
        x = sorted(long[x_dim].unique().tolist())
    else:
        x = []

    series = []
    groups = long.groupby(group_dims, sort=True) if group_dims else [((), long)]
    for key, group in groups:
        key = key if isinstance(key, tuple) else (key,)
        labels = dict(zip(group_dims, [_plain(k) for k in key], strict=True))
        if x_dim is not None:
            y = group.set_index(x_dim)["value"].groupby(level=0).mean().reindex(x)
        else:
            y = pd.Series([group["value"].mean()])
        series.append({"labels": labels, "y": _floats(y.to_numpy())})
        if len(series) >= MAX_SERIES:
            break

    return {
        "kind": "series",
        "file": file,
        "value_name": value_name,
        "rows": rows,
        "x_dim": x_dim,
        "x": [_plain(v) for v in x],
        "x_single": x_single,
        "spatial_dim": spatial_dim,
        "group_dims": group_dims,
        "series": series,
        "truncated": len(series) >= MAX_SERIES,
    }


def _column_dim(name: str, columns: list[str]) -> str:
    """The dimension of the columns of a wide file: node, edge or column."""
    path = dataset_path(name)
    if set(columns) <= {n["node"] for n in _nodes(path)}:
        return "node"
    if set(columns) <= {e["edge"] for e in _edges(path)}:
        return "edge"
    return "column"


def _rows(df: pd.DataFrame, limit: int = 2000) -> list[list[Any]]:
    return [[_plain(v) for v in row] for row in df.head(limit).itertuples(index=False)]


def _floats(values: np.ndarray) -> list[float | None]:
    return [None if not np.isfinite(v) else float(v) for v in values.astype(float)]


def _plain(value: Any) -> Any:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if not np.isfinite(value) else float(value)
    return value


# ---------- helpers ----------


def _nodes(path: Path) -> list[dict[str, Any]]:
    file = path / ENERGY_SYSTEM / "set_nodes.csv"
    if not file.exists():
        return []
    df = pd.read_csv(file)
    return [
        {
            "node": row["node"],
            "lon": _plain(row.get("lon")),
            "lat": _plain(row.get("lat")),
        }
        for row in df.to_dict("records")
    ]


def _edges(path: Path) -> list[dict[str, Any]]:
    file = path / ENERGY_SYSTEM / "set_edges.csv"
    if not file.exists():
        return []
    return [
        {str(key): value for key, value in row.items()}
        for row in pd.read_csv(file).to_dict("records")
    ]


def _meta(name: str) -> dict[str, Any]:
    file = META_PATH / f"{name}.json"
    if not file.exists():
        return {}
    return json.loads(file.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    """Read a text file that may be written in the platform's encoding.

    On Windows, sources.md is written in the system codepage rather than
    UTF-8, so fall back to it.
    """
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def _read_yaml(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _folder_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _inside(root: Path, name: str) -> Path:
    """root / name, refusing names that leave root."""
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise NotFound(f"Invalid name '{name}'.")
    return path
