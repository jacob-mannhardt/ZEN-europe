from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pandas as pd
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

from zen_europe.datasets.datasets.technology._cost_schema import (
    CO2_BASIS_UNITS,
    INDEX_NAMES,
    VALUE_COLUMNS,
)

# internal technology name -> DEA (Technology, category, input, size) row key.
# `size=None` means the technology varies by plant_size in the source data
# (looked up dynamically); a fixed string means the technology only exists at
# that one DEA size.
#
# Not ported (documented limitation): `oil_boiler_DH` -- the legacy script
# mapped it to the same DEA row as `waste_boiler_DH`, which looks like a
# copy-paste bug rather than an intentional simplification, so we drop it
# instead of repeating it. (`oil_boiler_DH` costs are still available via
# the LUW dataset.)
_MAIN_TECHS: dict[str, tuple[str, str, str, str | None]] = {
    "wind_onshore": ("Onshore wind turbine, utility", "renewable power", "wind", "large"),
    "wind_offshore": ("Offshore wind turbines", "renewable power", "wind", "large"),
    "wind_offshore_near_shore": ("Offshore wind turbines, nearshore", "renewable power", "wind", "large"),
    "photovoltaics": ("PV", "renewable power", "solar", "utility-scale, ground mounted"),
    "rooftop_photovoltaics": ("PV", "renewable power", "solar", "residential rooftop"),
    "rooftop_photovoltaics_com": ("PV", "renewable power", "solar", "commercial/industrial rooftop"),
    "natural_gas_turbine": ("Gas turbine, combined cycle", "extraction", "natural gas", "large"),
    "oc_natural_gas_turbine": ("Gas turbine, open cycle", "back pressure", "natural gas", "medium"),
    "hard_coal_plant": ("Coal power plant, supercritical", "extraction", "coal", "medium"),
    "natural_gas_boiler_DH": ("Gas boiler", "boiler", "natural gas", "medium"),
    "heat_pump_DH": ("Heat pump, air source", "heat pump", "electricity", None),
    "waste_boiler_DH": ("Waste boiler", "boiler", "waste", "small"),
    "biomass_boiler_DH": ("Biomass boiler", "boiler", "wood chips", "medium"),
    "electrode_boiler_DH": ("Electric boiler", "boiler", "electricity", None),
    "fuel_cell": ("Low temp PEM fuel cell", "back pressure", "hydrogen", "small"),
}
_PV_TECHS = {"photovoltaics", "rooftop_photovoltaics", "rooftop_photovoltaics_com"}
_SIZE_MAP = {"S": "small", "M": "medium", "L": "large"}
_SIZE_MAP_PV = {"S": "residential rooftop", "M": "commercial/industrial rooftop", "L": "utility-scale, ground mounted"}

# internal technology name -> DEA (technology label, building age) row key,
# for the individual (residential) heating installations dataset.
_IH_TECHS: dict[str, tuple[str, str]] = {
    "natural_gas_boiler": ("Natural gas boiler", "existing building"),
    "heat_pump": ("Heat pump, Air-to-water", "existing building"),
    "oil_boiler": ("Oil boiler (mineral oil fired, < 10 % FAME)", "existing building"),
    "biomass_boiler": ("Biomass boiler, automatic stoking , wood pellets or wood chips", "existing building"),
    "electrode_boiler": ("Electric heating", "new building"),
}
# DEA has no "small" building-level entry; only single-family houses (M) and
# apartment complexes (L) are reported.
_IH_SIZE_MAP = {"M": "single-family house", "L": "apartment complex"}

_SCENARIOS = {"min": "lower", "max": "upper", "ref": "ctrl"}
_COST_VAR_LABELS = {"capex": "Nominal investment", "fopex": "Fixed O&M", "vopex": "Variable O&M"}

# internal technology name -> DEA carbon-capture technology row key. Costs are
# reported per tCO2/h captured rather than per kW, so these use
# `CO2_BASIS_UNITS` instead of the power/heat schema.
_CCS_TECHS: dict[str, str] = {
    "DAC": "Solid Adsorption Direct Air Capture Plant ",
    "cement_post_comb": "Post-combustion carbon capture - Retrofit 4500 ton clinker per day cement kiln",
    "NG_DRI_CCS": "Post-combustion carbon capture - Retrofit 4500 ton clinker per day cement kiln",
    "BF_BOF_CCS": "Post-combustion carbon capture - Retrofit 4500 ton clinker per day cement kiln",
    "SMR_CCS": "Post-combustion carbon capture retrofit - 100 MW(th) WtE or biomass CHP plant",
}
# DAC has no reported variable O&M figure.
_CCS_COST_PARS: dict[str, dict[str, str]] = {
    "DAC": {
        "capex": "Specific investment [mill €/(tCO2/hour)] (CO2 output)",
        "fopex": "Fixed O&M [mill €/(tCO2/hour)]",
    },
    "_default": {
        "capex": "Specific investment [mill €/[tCO2/hour]] (CO2 output)",
        "fopex": "Fixed O&M [mill €/[tCO2/hour]] (CO2 output)",
        "vopex": "Variable O&M [€/tCO2] (CO2 output)",
    },
}
_CCS_SCENARIOS = {"min": "Lower", "max": "Upper", "ref": "Est"}

# internal technology name -> DEA renewable-fuel technology row key. All
# reported on a Euro/kW(h)-of-output basis, so they fit the power/heat schema
# once converted; (par_string, multiplier_to_schema_unit) per technology and
# variable. `fischer_tropsch`'s "Fixed O&M" figure is priced per MWh of
# output rather than per MW/year of capacity (looks like a unit labeling
# error in the source spreadsheet) and `electrolysis`'s is a percentage of
# capex per year rather than an absolute figure -- both are left out, as the
# legacy script did.
_RF_TECHS: dict[str, str] = {
    "methanol_from_biomass": "Bio Methanol",
    "methanol_from_hydrogen": "Methanol from hydrogen and carbon dioxide",
    "haber_bosch": "Green Ammonia plant: Hydrogen to ammonia (excl. electrolyzer and excl. ASU)",
    "fischer_tropsch": "Hydrogen to Jet Fuel",
    "pyrolysis": "Slow pyrolysis for production of biochar, pyrolysis oil and gas from straw",
    "methanation": "SNG from Biogas",
    "gasification": "Gasifier, biomass, bio-SNG, medium - large scale",
    "electrolysis": "Hydrogen production via PEMEC electrolysis for 100 MW plant",
    "anaerobic_digestion": "Biogas plant, Basic plant, large [~ 6,000 Nm3 CH4/h]",
    "biomethane_conversion": "Biogas upgrading - Amine scrubber [~6,000 Nm3 CH4/h)",
}
_RF_COST_PARS: dict[str, dict[str, tuple[str, float]]] = {
    "methanol_from_biomass": {
        "capex": ("Specific investment [M€ /MW Methanol]", 1000.0),
        "fopex": ("Fixed O&M [M€ /MW/year Methanol]", 1000.0),
        "vopex": ("Variable O&M [€ /MWh methanol]", 1.0),
    },
    "methanol_from_hydrogen": {
        "capex": ("Specific investment [M€/MW-methanol]", 1000.0),
        "fopex": ("Fixed O&M [k€/[MW-methanol/year]]", 1.0),
        "vopex": ("Variable O&M [€/MWh-methanol]", 1.0),
    },
    "haber_bosch": {
        "capex": ("Specific investment [M€ /MW Ammonia output]", 1000.0),
        "fopex": ("Fixed O&M [k€/MW Ammonia/year]", 1.0),
        "vopex": ("Variable O&M [€/MWh Ammonia]", 1.0),
    },
    "fischer_tropsch": {
        "capex": ("Specific investment [M€ /MW Liquids/year]", 1000.0),
        "vopex": ("Variable O&M [€ /MWH Liquids]", 1.0),
    },
    "pyrolysis": {
        "capex": ("Specific investment [M€ /MW] output from pyrolysis process", 1000.0),
        "fopex": ("Fixed O&M ([M€ /MW/year] output from pyrolysis process", 1000.0),
        "vopex": ("Variable O&M ([€ /MWh] output from pyrolysis process)", 1.0),
    },
    "methanation": {
        "capex": ("Specific investment [M€ /MW SNG]", 1000.0),
        "fopex": ("Fixed O&M [M€ /MW/year SNG]", 1000.0),
        "vopex": ("Variable O&M [€ /MWh SNG]", 1.0),
    },
    "gasification": {
        "capex": ("Specific investment [M€/MWth]", 1000.0),
        "fopex": ("Fixed O&M [€/MWth/year]", 1 / 1000),
        "vopex": ("Variable O&M [€/MWhth]", 1.0),
    },
    "electrolysis": {
        "capex": ("Specific investment [€ / kW of total input_e]", 1.0),
        "vopex": ("Variable O&M [€ / kWh of total input]", 1000.0),
    },
    "anaerobic_digestion": {
        "capex": ("Specific investment [mill. €/MW output]", 1000.0),
        # empirical, plant-specific conversion factor from the legacy script
        # (EUR/ton-input/year -> Euro/kW/year for this reference plant size)
        "fopex": ("- of which O&M, excl el. and heat [€/(ton input/year)]", 67.59 / 3.36),
        "vopex": ("Variable O&M [€/GJ output]", 3.6),  # 1 MWh = 3.6 GJ
    },
    "biomethane_conversion": {
        "capex": ("Specific investment, upgrading and methane reduction [k €/MW output]", 1.0),
        "fopex": (
            "- of which fixed O&M costs upgrading and methane reduction, "
            "excl. el. and heat [k€/MW output/year]",
            1.0,
        ),
        "vopex": ("Variable O&M [€/GJ output]", 3.6),
    },
}
_RF_SCENARIOS_DEFAULT = {"min": "Lower", "max": "Upper", "ref": "ctrl"}
# anaerobic_digestion/biomethane_conversion use "Est" for the reference
# scenario where every other DEA renewable-fuel technology uses "ctrl" -- the
# legacy script always looked for "ctrl" and so silently never found a
# reference-scenario value for these two technologies; ported correctly here.
_RF_SCENARIOS_ALT = {"min": "Lower", "max": "Upper", "ref": "Est"}
_RF_ALT_SCENARIO_TECHS = {"anaerobic_digestion", "biomethane_conversion"}


def _dea_size(plant_size: str, technology: str) -> str:
    return _SIZE_MAP_PV[plant_size] if technology in _PV_TECHS else _SIZE_MAP[plant_size]


def _convert_main_unit(unit_src: str, variable: str) -> float:
    """Multiplier from a DEA source unit to this package's standard unit."""
    if variable == "capex" and unit_src in ("MEUR/MW_e", "MEUR/MW_h"):
        return 1000.0  # MEUR/MW -> Euro/kW
    if variable == "fopex" and unit_src in ("EUR/MW_e/y", "EUR/MW_h/y"):
        return 1 / 1000  # EUR/MW/y -> Euro/kW/year
    if variable == "vopex" and unit_src in ("EUR/MWh_e", "EUR/MWh_h"):
        return 1.0  # already Euro/MWh
    raise ValueError(f"Unexpected DEA unit '{unit_src}' for variable '{variable}'")


def _convert_ccs_unit(unit_src: str, variable: str) -> float:
    """Multiplier from a DEA carbon-capture source unit to `CO2_BASIS_UNITS`.

    Source unit strings are inconsistently bracketed across technologies
    (`millEUR/(tCO2/hour)` vs `millEUR/[tCO2/hour`), so this matches on
    normalized substrings rather than exact strings.
    """
    normalized = unit_src.lower().replace(" ", "")
    multiplier = 1e6 if "mill" in normalized else 1.0
    if variable in ("capex", "fopex") and "tco2/hour" in normalized:
        return multiplier
    if variable == "vopex" and normalized == "eur/tco2":
        return multiplier
    raise ValueError(f"Unexpected DEA CCS unit '{unit_src}' for variable '{variable}'")


class DEA(Dataset[pd.DataFrame]):
    """Danish Energy Agency (DEA) technology catalogue cost data.

    Covers utility-scale power/district-heating technologies, individual
    (residential) heating installations, carbon-capture technologies, and
    renewable-fuel production routes.

    Carbon-capture technologies are reported on a Euro/tCO2(/h) basis rather
    than Euro/kW; their rows carry `CO2_BASIS_UNITS` in the `unit` column
    instead of the power/heat schema, and `TechnologyCostDatabase` reads that
    unit back out of the data rather than assuming a fixed one per variable.
    DEA's oxy-fuel capture and CO2 transport/storage/liquefaction entries are
    *not* included (out of scope for a technology cost database: they price
    logistics infrastructure, not a conversion technology).

    Raw data is a frozen CSV snapshot of DEA's "alldata_flat" export (rather
    than a live download, as the legacy script did), for reproducibility.
    """

    name = "dea"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Technology Data for Generation of Electricity and District Heating",
            author=["Danish Energy Agency", "Energinet"],
            publication="Danish Energy Agency",
            publication_year=2024,
            url="https://ens.dk/en/our-services/projections-and-models/technology-data",
            note=(
                "Also includes 'Technology Data for Individual Heating Installations' "
                "from the same publisher/URL, for residential heating technologies."
            ),
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path / "03-technology" / "cost" / "dea"

    def _set_data(self) -> pd.DataFrame:
        financial = self._read_dea_csv(self.path / "dea_power_district_heat_financial.csv")
        technical = self._read_dea_csv(self.path / "dea_power_district_heat_technical.csv")
        ih_financial = self._read_dea_csv(self.path / "dea_individual_heating_financial.csv")
        ih_technical = self._read_dea_csv(self.path / "dea_individual_heating_technical.csv")
        ccs_financial = self._read_dea_csv(self.path / "dea_ccs_financial.csv")
        ccs_technical = self._read_dea_csv(self.path / "dea_ccs_technical.csv")
        rf_financial = self._read_dea_csv(self.path / "dea_renewable_fuels_financial.csv")
        rf_technical = self._read_dea_csv(self.path / "dea_renewable_fuels_technical.csv")

        rows: list[tuple] = []
        rows += self._parse_main(financial, technical)
        rows += self._parse_individual_heating(ih_financial, ih_technical)
        rows += self._parse_ccs(ccs_financial, ccs_technical)
        rows += self._parse_renewable_fuels(rf_financial, rf_technical)

        data = pd.DataFrame(rows, columns=INDEX_NAMES + VALUE_COLUMNS)
        data = data.drop_duplicates(subset=INDEX_NAMES)
        return data.set_index(INDEX_NAMES).sort_index()

    @staticmethod
    def _read_dea_csv(path: Path) -> pd.DataFrame:
        """Read a DEA raw csv, dropping rows whose `val` is a non-numeric
        placeholder (e.g. "-" for "not applicable")."""
        df = pd.read_csv(path)
        df["val"] = pd.to_numeric(df["val"], errors="coerce")
        return df.dropna(subset=["val"])

    def _parse_main(self, financial: pd.DataFrame, technical: pd.DataFrame) -> list[tuple]:
        rows: list[tuple] = []
        for technology, (dea_tech, category, dea_input, fixed_size) in _MAIN_TECHS.items():
            for plant_size in ("S", "M", "L"):
                size = _dea_size(plant_size, technology)
                if fixed_size is not None and size != fixed_size:
                    continue
                label = " - ".join([dea_tech, category, dea_input, size])
                tech_rows = financial[financial["Technology"] == label]
                if tech_rows.empty:
                    continue
                for scenario, est in _SCENARIOS.items():
                    for variable, var_label in _COST_VAR_LABELS.items():
                        par = self._find_cost_par(tech_rows, var_label)
                        if par is None:
                            continue
                        sel = tech_rows[(tech_rows["par"] == par) & (tech_rows["est"] == est)]
                        if sel.empty:
                            continue
                        unit_src = sel["unit"].iloc[0]
                        multiplier = _convert_main_unit(unit_src, variable)
                        schema_unit = {"capex": "Euro/kW", "fopex": "Euro/kW/year", "vopex": "Euro/MWh"}[variable]
                        for _, row in sel.iterrows():
                            rows.append(
                                (
                                    technology, plant_size, scenario, variable, int(row["year"]),
                                    float(row["val"]) * multiplier, schema_unit,
                                    int(row["priceyear"]), float(row["val"]), unit_src,
                                )
                            )
                rows += self._parse_main_tech_vars(technical, label, technology, plant_size)
        return rows

    @staticmethod
    def _find_cost_par(tech_rows: pd.DataFrame, var_label: str) -> str | None:
        """DEA reports electric- and heat-basis figures under different par
        strings; prefer the electric one, fall back to heat."""
        for suffix in ("MW_e", "MW_h") if var_label != "Variable O&M" else ("MWh_e", "MWh_h"):
            money = "MEUR" if var_label == "Nominal investment" else "EUR"
            year_str = "/y" if var_label == "Fixed O&M" else ""
            par = f"{var_label} (*total) [{money}/{suffix}{year_str}]"
            if (tech_rows["par"] == par).any():
                return par
        return None

    @staticmethod
    def _parse_main_tech_vars(
        technical: pd.DataFrame, label: str, technology: str, plant_size: str
    ) -> list[tuple]:
        tech_rows = technical[technical["Technology"] == label]
        if tech_rows.empty:
            return []
        rows: list[tuple] = []
        tech_pars = {
            "efficiency": ["Electrical efficiency (net, name plate) []", "Heat efficiency (net, name plate) []"],
            "lifetime": ["Technical lifetime [years]"],
            "construction_time": ["Construction time [years]"],
        }
        schema_units = {"efficiency": "-", "lifetime": "years", "construction_time": "years"}
        for variable, candidate_pars in tech_pars.items():
            for par in candidate_pars:
                sel = tech_rows[tech_rows["par"] == par]
                if sel.empty:
                    continue
                for scenario, est in _SCENARIOS.items():
                    scen_sel = sel[sel["est"] == est]
                    for _, row in scen_sel.iterrows():
                        rows.append(
                            (
                                technology, plant_size, scenario, variable, int(row["year"]),
                                float(row["val"]), schema_units[variable],
                                None, float(row["val"]), schema_units[variable],
                            )
                        )
                break
        return rows

    def _parse_individual_heating(
        self, financial: pd.DataFrame, technical: pd.DataFrame
    ) -> list[tuple]:
        rows: list[tuple] = []
        for technology, (dea_tech, buildage) in _IH_TECHS.items():
            for plant_size, size in _IH_SIZE_MAP.items():
                label = f"{dea_tech} - {size} - {buildage}"
                fin_rows = financial[financial["Technology"] == label]
                tech_rows = technical[technical["Technology"] == label]
                if fin_rows.empty:
                    continue
                capacity_kw = self._ih_capacity_kw(tech_rows)
                if capacity_kw is None:
                    continue
                for scenario, est in _SCENARIOS.items():
                    rows += self._parse_ih_costs(fin_rows, technology, plant_size, scenario, est, capacity_kw)
                rows += self._parse_ih_tech_vars(tech_rows, technology, plant_size)
        return rows

    @staticmethod
    def _ih_capacity_kw(tech_rows: pd.DataFrame) -> float | None:
        """Per-unit heat production capacity [kW], needed to convert DEA's
        per-appliance ("/unit") capex and fopex figures to a per-kW basis."""
        sel = tech_rows[
            (tech_rows["par"] == "Heat production capacity for one unit [kW_h]")
            & (tech_rows["est"] == "ctrl")
        ]
        if sel.empty:
            return None
        return float(sel["val"].iloc[0])

    @staticmethod
    def _parse_ih_costs(
        fin_rows: pd.DataFrame, technology: str, plant_size: str, scenario: str, est: str, capacity_kw: float
    ) -> list[tuple]:
        rows: list[tuple] = []
        par_by_var = {
            "capex": "Nominal investment (*total) [k€/unit, 2020]",
            "fopex": "Fixed O&M (*total) [€/unit/y, 2020]",
            "vopex": "Variable O&M (*total) [€/kWh, 2020]",
        }
        for variable, par in par_by_var.items():
            sel = fin_rows[(fin_rows["par"] == par) & (fin_rows["est"] == est)]
            if sel.empty:
                continue
            for _, row in sel.iterrows():
                value_src = float(row["val"])
                if variable == "capex":
                    value = value_src * 1000 / capacity_kw  # k Euro/unit -> Euro/kW
                    unit = "Euro/kW"
                elif variable == "fopex":
                    value = value_src / capacity_kw  # Euro/unit/y -> Euro/kW/year
                    unit = "Euro/kW/year"
                else:
                    value = value_src * 1000  # Euro/kWh -> Euro/MWh
                    unit = "Euro/MWh"
                rows.append(
                    (
                        technology, plant_size, scenario, variable, int(row["year"]),
                        value, unit, int(row["priceyear"]), value_src, par,
                    )
                )
        return rows

    @staticmethod
    def _parse_ih_tech_vars(tech_rows: pd.DataFrame, technology: str, plant_size: str) -> list[tuple]:
        rows: list[tuple] = []
        tech_pars = {
            "efficiency": "Heat efficiency (annual average, net) [p.u.]",
            "lifetime": "Technical economic lifetime [years]",
        }
        schema_units = {"efficiency": "-", "lifetime": "years"}
        for variable, par in tech_pars.items():
            sel = tech_rows[(tech_rows["par"] == par) & (tech_rows["est"] == "ctrl")]
            for _, row in sel.iterrows():
                for scenario in _SCENARIOS:
                    rows.append(
                        (
                            technology, plant_size, scenario, variable, int(row["year"]),
                            float(row["val"]), schema_units[variable],
                            None, float(row["val"]), schema_units[variable],
                        )
                    )
        return rows

    def _parse_ccs(self, financial: pd.DataFrame, technical: pd.DataFrame) -> list[tuple]:
        rows: list[tuple] = []
        for technology, dea_label in _CCS_TECHS.items():
            cost_pars = _CCS_COST_PARS.get(technology, _CCS_COST_PARS["_default"])
            fin_rows = financial[financial["Technology"] == dea_label]
            tech_rows = technical[technical["Technology"] == dea_label]
            if fin_rows.empty:
                continue
            for scenario, est in _CCS_SCENARIOS.items():
                for variable, par in cost_pars.items():
                    sel = fin_rows[(fin_rows["par"] == par) & (fin_rows["est"] == est)]
                    if sel.empty:
                        continue
                    unit_src = sel["unit"].iloc[0]
                    multiplier = _convert_ccs_unit(unit_src, variable)
                    for _, row in sel.iterrows():
                        rows.append(
                            (
                                technology, "M", scenario, variable, int(row["year"]),
                                float(row["val"]) * multiplier, CO2_BASIS_UNITS[variable],
                                int(row["priceyear"]), float(row["val"]), unit_src,
                            )
                        )
            rows += self._parse_lifetime_and_construction_time(tech_rows, technology, "M", _CCS_SCENARIOS)
        return rows

    def _parse_renewable_fuels(self, financial: pd.DataFrame, technical: pd.DataFrame) -> list[tuple]:
        financial = financial.copy()
        financial["Technology"] = financial["Technology"].str.strip()
        technical = technical.copy()
        technical["Technology"] = technical["Technology"].str.strip()

        rows: list[tuple] = []
        for technology, dea_label in _RF_TECHS.items():
            scenarios = _RF_SCENARIOS_ALT if technology in _RF_ALT_SCENARIO_TECHS else _RF_SCENARIOS_DEFAULT
            fin_rows = financial[financial["Technology"] == dea_label]
            tech_rows = technical[technical["Technology"] == dea_label]
            if fin_rows.empty:
                continue
            schema_units = {"capex": "Euro/kW", "fopex": "Euro/kW/year", "vopex": "Euro/MWh"}
            for scenario, est in scenarios.items():
                for variable, (par, multiplier) in _RF_COST_PARS[technology].items():
                    sel = fin_rows[(fin_rows["par"] == par) & (fin_rows["est"] == est)]
                    if sel.empty:
                        continue
                    for _, row in sel.iterrows():
                        rows.append(
                            (
                                technology, "M", scenario, variable, int(row["year"]),
                                float(row["val"]) * multiplier, schema_units[variable],
                                int(row["priceyear"]), float(row["val"]), par,
                            )
                        )
            rows += self._parse_lifetime_and_construction_time(tech_rows, technology, "M", scenarios)
        return rows

    @staticmethod
    def _parse_lifetime_and_construction_time(
        tech_rows: pd.DataFrame, technology: str, plant_size: str, scenarios: dict[str, str]
    ) -> list[tuple]:
        rows: list[tuple] = []
        tech_pars = {"lifetime": "Technical lifetime [years]", "construction_time": "Construction time [years]"}
        for variable, par in tech_pars.items():
            sel = tech_rows[tech_rows["par"] == par]
            if sel.empty:
                continue
            for scenario, est in scenarios.items():
                scen_sel = sel[sel["est"] == est]
                for _, row in scen_sel.iterrows():
                    rows.append(
                        (
                            technology, plant_size, scenario, variable, int(row["year"]),
                            float(row["val"]), "years", None, float(row["val"]), "years",
                        )
                    )
        return rows

    # -------- methods ------------------------

    def get_costs(self) -> pd.DataFrame:
        """Return the parsed, standardized DEA cost/tech data (see `_cost_schema`)."""
        return self.data.copy()
