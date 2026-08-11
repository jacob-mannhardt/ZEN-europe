"""Aggregated technology cost database.

Combines capex/opex/efficiency/lifetime/construction-time figures from
several independent technology-cost sources (DEA, TYNDP, DIW, LUW, EUREF,
Potencia) into a single queryable database, following the same "many
agencies, one schema" approach as the legacy ``agg_financial_parameters.py``
script this class replaces.

Not ported from the legacy script (documented limitations):
    - The ETRI, BNEF, NREL and IRENA sources: these were already
      unimplemented stubs in the legacy script, so there was nothing to port.
    - DEA's CO2 transport/storage/liquefaction entries: these were never
      parsed by the legacy script either, price logistics infrastructure
      rather than a standalone conversion technology, and the technologies
      that could theoretically consume them (`carbon_pipeline`,
      `carbon_storage`) already source their costs from a separate, active
      pipeline (``costs_additional_technologies.xlsx``).
    - `oil_boiler_DH` (DEA mapped it to the same row as `waste_boiler_DH` in
      the legacy script - looks like a bug, not reproduced here).


Note: DEA's and LUW's carbon-capture technologies (DAC and DEA's retrofit
post-combustion capture) are reported on a Euro/tCO2(/h) basis rather than
Euro/kW; the `unit` returned by `get_capex_specific_conversion` etc.
reflects whichever basis the technology actually uses (see `_unit_for`), it
is not always `Euro/kW`.

Note: Potencia reports a single point estimate per technology/year (no
min/max spread, ``scenario="ref"`` only) at up to four plant sizes, of which
this database uses S/M/L.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset, Element

from zen_creator import Attribute, DatasetCollection
from zen_creator.utils.attribute import SourceInformation
from zen_creator.utils.settings import Settings

from zen_europe.datasets.datasets.financial.ECB import ECBInflation
from zen_europe.datasets.datasets.financial._cost_schema import (
    COST_VARIABLES,
    STANDARD_UNITS,
    YEARS,
)
from zen_europe.datasets.datasets.financial.dea import DEA
from zen_europe.datasets.datasets.financial.diw import DIW
from zen_europe.datasets.datasets.financial.euref import EUREF
from zen_europe.datasets.datasets.financial.luw import LUW
from zen_europe.datasets.datasets.financial.potencia import Potencia
from zen_europe.datasets.datasets.financial.tyndp_technology_cost import TYNDPTechnologyCost

_AGENCY_DATASETS = {
    "dea": DEA,
    "tyndp": TYNDPTechnologyCost,
    "diw": DIW,
    "luw": LUW,
    "euref": EUREF,
    "potencia": Potencia,
}
_METRICS = ("mean", "median", "min", "max")


class TechnologyCostDatabase(DatasetCollection):
    """Aggregated capex/opex/efficiency/lifetime technology cost database."""

    name = "technology_cost_database"

    def __init__(self, settings: Settings, source_path: Path | str):
        self.settings = settings
        super().__init__(source_path=source_path)
        self._inflation = ECBInflation(source_path=self.source_path)

    def _get_data(self) -> Dict[str, Dataset[Any]]:
        """Load all available agency cost data sources."""
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")

        return {name: cls(self.source_path) for name, cls in _AGENCY_DATASETS.items()}

    # -------- outward-facing accessors ------------------

    def get_capex_specific_conversion(
        self, element: Element, plant_size: str = "M", metric: str = "mean"
    ) -> Attribute:
        """Specific investment cost [Euro/kW] for `element`'s technology."""
        return self._set_technology_attribute(
            element, element.capex_specific_conversion, "capex", plant_size, metric,
            description="specific investment cost (CAPEX)", annual_values=True
        )

    def get_opex_specific_fixed(
        self, element: Element, plant_size: str = "M", metric: str = "mean"
    ) -> Attribute:
        """Fixed operational cost [Euro/kW/year] for `element`'s technology."""
        return self._set_technology_attribute(
            element, element.opex_specific_fixed, "fopex", plant_size, metric,
            description="fixed operational cost", annual_values=True
        )

    def get_opex_specific_variable(
        self, element: Element, plant_size: str = "M", metric: str = "mean"
    ) -> Attribute:
        """Variable operational cost [Euro/MWh] for `element`'s technology."""
        return self._set_technology_attribute(
            element, element.opex_specific_variable, "vopex", plant_size, metric,
            description="variable operational cost", annual_values=False
        )

    def get_lifetime(
        self, element: Element, plant_size: str = "M", metric: str = "median"
    ) -> Attribute:
        """Technical lifetime [years] for `element`'s technology."""
        return self._set_technology_attribute(
                    element, element.lifetime, "lifetime", plant_size, metric,
                    description="technical lifetime", annual_values=True
                )

    def get_construction_time(
        self, element: Element, plant_size: str = "M", metric: str = "median"
    ) -> Attribute:
        """Construction time [years] for `element`'s technology."""
        return self._set_technology_attribute(
                    element, element.construction_time, "construction_time", plant_size, metric,
                    description="construction time", annual_values=True
                )

    def get_efficiency(
        self, technology: str, plant_size: str = "M", metric: str = "mean",
        reference_year: int | None = None,
    ) -> pd.Series:
        """Conversion efficiency [-] for `technology`, indexed by year.

        Returned directly as a `pd.Series` rather than an `Attribute`, since
        efficiency is technology-specific (e.g. it feeds a `conversion_factor`
        computation together with carrier-specific heating values) and has no
        single common attribute to populate across all conversion technologies.
        """
        return self._aggregate(
            technology, "efficiency", 
            plant_size, metric, 
            reference_year or self.settings.time.reference_year
        )

    def check_if_available(self, technology: str, variable: str | None = None) -> bool:
        """Whether any agency reports data for `technology` (optionally `variable`)."""
        for dataset in self.data.values():
            df = cast(Any, dataset).get_costs()
            if technology not in df.index.get_level_values("technology"):
                continue
            if variable is None:
                return True
            if variable in df.xs(technology, level="technology").index.get_level_values("variable"):
                return True
        return False

    def export_cost_table(
        self, path: Path, technologies: list[str] | None = None,
        plant_size: str = "M", reference_year: int | None = None,
    ) -> pd.DataFrame:
        """Export a min/mean/max cost table (capex, fopex, vopex) to Excel.

        This is the numeric-export counterpart of the legacy script's
        `save_cost_curves`; the matplotlib `plot_cost_curves` figure export
        was intentionally not ported.
        """
        reference_year = reference_year or self.settings.time.reference_year
        if technologies is None:
            technologies = sorted(self._available_technologies())

        table: dict[tuple[str, str, str], pd.Series] = {}
        units: dict[tuple[str, str, str], str] = {}
        for technology in technologies:
            for variable in COST_VARIABLES:
                for metric in ("min", "mean", "max"):
                    series = self._aggregate(
                        technology, variable, plant_size, metric, reference_year)
                    if series.empty:
                        continue
                    key = (technology, variable, metric)
                    table[key] = series
                    units[key] = self._unit_for(technology, variable, plant_size)
        cost_df = pd.DataFrame(table).T
        cost_df.index.names = ["technology", "variable", "metric"]
        cost_df.insert(0, "unit", pd.Series(units))
        cost_df.to_excel(path)
        return cost_df

    # -------- aggregation internals ------------------

    def _set_technology_attribute(
        self, element: Element, attribute: Attribute, variable: str,
        plant_size: str, metric: str, description: str, annual_values: bool = True
    ) -> Attribute:
        reference_year = element.settings.time.reference_year
        series = self._aggregate(
            element.name, variable, plant_size, metric, reference_year)
        agencies = self._extract_agencies(element.name, variable, plant_size)
        source = SourceInformation(
            description=(
                f"{description.capitalize()} for '{element.name}' is the {metric} across "
                f"for the agencies {', '.join(agencies)} reporting data for this "
                f"technology at plant size '{plant_size}'. Monetary values are rebased to "
                f"{reference_year} EUR using ECB HICP inflation."
            ),
            metadata=self.metadata,
        )
        if series.empty:
            return attribute.set_data(source=source)

        optimization_years = pd.Index(element.settings.time.get_optimization_years())
        if annual_values:
            df = self._reindex_to_years(series, optimization_years)
            default_value = float(df.loc[reference_year])
            if len(df.unique()) == 1:
                df = None
            else:
                df.index.name = "year"
                df.name = attribute.name
            yearly_variations = None
        else:
            default_value = float(
                self._reindex_to_years(series, 
                                    pd.Index([reference_year])).loc[reference_year])
            yearly_variations = self._reindex_to_years(
                series, optimization_years) / default_value
            yearly_variations.index.name = "year"
            yearly_variations.name = attribute.name
            df = None
        return attribute.set_data(
            source=source,
            default_value=default_value,
            df=df,
            unit=self._unit_for(element.name, variable, plant_size),
            yearly_variations_df=yearly_variations,
        )

    def _aggregate(
        self, 
        technology: str, 
        variable: str, 
        plant_size: str, 
        metric: str, 
        reference_year: int,
    ) -> pd.Series:
        """Aggregate `variable` for `technology` across agencies/scenarios.

        Cost variables (capex/fopex/vopex) are inflation-adjusted to
        `reference_year` before aggregating; technology variables
        (efficiency/lifetime/construction_time) need no such adjustment.
        Returns a `pd.Series` indexed by year, empty if no agency has data.
        """
        if metric not in _METRICS:
            raise ValueError(f"metric must be one of {_METRICS}, got '{metric}'")

        rows = self._collect_rows(technology, variable, plant_size)
        if rows.empty:
            return pd.Series(dtype=float)

        if variable in COST_VARIABLES:
            rows = rows.assign(
                value=[
                    value * self._inflation.get_inflation_rate(
                        int(money_year_src), reference_year)
                    for value, money_year_src in zip(rows["value"], rows["money_year_src"])
                ]
            )

        # one column per (agency, scenario) source series, interpolated over its own reported years
        pivoted = rows.pivot_table(index="year", columns=["agency", "scenario"], values="value")
        pivoted = pivoted.reindex(sorted(set(pivoted.index) | set(YEARS))).sort_index()
        pivoted = pivoted.interpolate(method="index", limit_direction="both")
        pivoted = pivoted.loc[pivoted.index.isin(YEARS)]

        ref_columns = [col for col in pivoted.columns if col[1] == "ref"]
        reference = pivoted[ref_columns].mean(axis=1) if ref_columns else pivoted.mean(axis=1)
        if metric == "min":
            candidate = (pivoted.xs("min", level="scenario", axis=1) 
            if "min" in pivoted.columns.get_level_values(
                "scenario") else pivoted[ref_columns])
            result = candidate.min(axis=1)
            # guard against a reported "min" scenario that isn't actually below "ref"
            result = result.where(result <= reference, reference)
        elif metric == "max":
            candidate = (pivoted.xs("max", level="scenario", axis=1) 
            if "max" in pivoted.columns.get_level_values(
                "scenario") else pivoted[ref_columns])
            result = candidate.max(axis=1)
            result = result.where(result >= reference, reference)
        elif metric == "median":
            result = pivoted.median(axis=1)
        else:
            result = pivoted.mean(axis=1)
        result.index.name = "year"
        return result

    def _extract_agencies(self, technology: str, variable: str, plant_size: str) -> set[str]:
        """Return the set of agencies reporting data for `technology`/`variable`."""
        rows = self._collect_rows(technology, variable, plant_size)
        return set(rows["agency"].unique())
    
    def _collect_rows(self, technology: str, variable: str, plant_size: str) -> pd.DataFrame:
        frames = []
        for agency, dataset in self.data.items():
            df = cast(Any, dataset).get_costs()
            key = (technology, plant_size, slice(None), variable, slice(None))
            try:
                sel = df.loc[key]
            except KeyError:
                continue
            if sel.empty:
                continue
            sel = sel.reset_index()
            sel["agency"] = agency
            frames.append(sel)
        if not frames:
            return pd.DataFrame(
                columns=["agency", "scenario", "year", "value", "money_year_src"])
        return pd.concat(frames, ignore_index=True)

    def _unit_for(self, technology: str, variable: str, plant_size: str) -> str:
        """The unit actually reported for `technology`/`variable`.

        Most technologies use `STANDARD_UNITS[variable]`, but a few (DEA's
        carbon-capture technologies) report costs on a different physical
        basis (Euro/tCO2 rather than Euro/kW) -- the data itself is
        authoritative, `STANDARD_UNITS` is only a fallback for technologies
        with no data at all.
        """
        rows = self._collect_rows(technology, variable, plant_size)
        if rows.empty:
            return STANDARD_UNITS[variable]
        return str(rows["unit"].iloc[0])

    def _available_technologies(self) -> set[str]:
        technologies: set[str] = set()
        for dataset in self.data.values():
            df = cast(Any, dataset).get_costs()
            technologies.update(df.index.get_level_values("technology"))
        return technologies

    @staticmethod
    def _reindex_to_years(series: pd.Series, years: pd.Index) -> pd.Series:
        combined_index = sorted(set(series.index) | set(years))
        reindexed = series.reindex(combined_index).interpolate(
            method="index", limit_direction="both")
        return reindexed.loc[years]
