from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pandas as pd
from zen_creator import Attribute, SourceInformation, Technology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData


class TechnologyDiffusionMannhardt(Dataset[pd.DataFrame]):
    """
    Maximum technology diffusion rates, based on Mannhardt et al. (2024).

    Technologies are grouped into four categories. Each category takes the
    historically observed diffusion rate of one reference technology.
    """

    name = "technology_diffusion_mannhardt"

    # diffusion rate per category and the reference technology it is derived from
    DIFFUSION_RATES = {
        "LOW": 0.1,
        "MEDIUM": 0.13,
        "HIGH": 0.29,
        "VERY_HIGH": 0.4,
    }
    REFERENCE_TECHNOLOGIES = {
        "LOW": "wind offshore",
        "MEDIUM": "wind onshore",
        "HIGH": "photovoltaics",
        "VERY_HIGH": "battery electric vehicles",
    }

    LOW = [
        "hard_coal_plant",
        "nuclear",
        "reservoir_hydro",
        "wind_offshore",
        "lignite_coal_plant",
        "pumped_hydro",
        "hydrogen_storage",
        "natural_gas_storage",
    ]
    MEDIUM = [
        "wind_onshore",
        "natural_gas_turbine",
        "hard_coal_plant_CCS",
        "natural_gas_turbine_CCS",
        "run-of-river_hydro",
        "biomass_plant",
        "biomass_plant_CCS",
        "oil_plant",
        "waste_plant",
        "lng_terminal",
        "natural_gas_boiler_DH",
        "heat_pump_DH",
        "oil_boiler_DH",
        "waste_boiler_DH",
        "biomass_boiler_DH",
        "hard_coal_boiler_DH",
        "electrode_boiler_DH",
        "district_heating_grid",
        "electrolysis",
        "fuel_cell",
        "gasification",
        "gasification_CCS",
        "SMR",
        "SMR_CCS",
        "biomethane_conversion",
        "power_line",
        "natural_gas_pipeline",
        "carbon_pipeline",
        "hydrogen_pipeline",
        "coal_to_cement_fuel",
        "biomass_to_cement_fuel",
        "waste_to_cement_fuel",
        "hydrogen_to_cement_fuel",
        "olefin_from_methanol",
        "diesel_ICE_ship",
        "ammonia_ICE_ship",
        "methanol_ICE_ship",
        "hydrogen_ICE_ship",
        "hydrogen_FC_ship",
        "BF_BOF",
        "NG_DRI",
        "H2_DRI",
        "carbon_storage",
        "BF_BOF_CCS",
        "NG_DRI_CCS",
        "cement_post_comb",
        "methanol_from_natural_gas",
        "methanol_from_hydrogen",
        "methanol_from_biomass",
        "fischer_tropsch",
        "DAC",
        "pyrolysis",
        "refining",
        "methanation",
        "oil_to_gasoline_conversion",
        "oil_to_diesel_conversion",
        "oil_to_kerosene_conversion",
    ]
    HIGH = [
        "photovoltaics",
        "natural_gas_boiler",
        "heat_pump",
        "oil_boiler",
        "biomass_boiler",
        "hard_coal_boiler",
        "electrode_boiler",
        "battery",
        "HDT_BET",
        "HDT_diesel",
        "HDT_FCEV",
    ]
    VERY_HIGH = [
        "BEV",
        "ICE_diesel",
        "ICE_petrol",
        "HEV",
        "PHEV",
        "ICE_cng",
    ]

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)
        self.categories = {
            technology: category
            for category in self.DIFFUSION_RATES
            for technology in getattr(self, category)
        }

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Understanding the vicious cycle of myopic foresight and "
                "constrained technology deployment in transforming the "
                "European energy system"
            ),
            author=["Jacob Mannhardt", "Paolo Gabrielli", "Giovanni Sansavini"],
            publication="iScience",
            publication_year=2024,
            url="https://www.cell.com/iscience/fulltext/S2589-0042(24)02594-X",
            doi="https://doi.org/10.1016/j.isci.2024.111369",
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> dict[str, pd.DataFrame]:
        """
        No data to be set.
        """
        data = {}
        return data

    # -------- methods ------------------------
    def get_category(self, technology: Technology) -> str:
        """
        Get the diffusion category of a technology.
        """
        if technology.name not in self.categories:
            raise ValueError(
                f"No diffusion rate is available for technology '{technology.name}'."
            )
        return self.categories[technology.name]

    def get_max_diffusion_rate(self, technology: Technology) -> Attribute:
        """
        Get the maximum diffusion rate of a technology.
        """
        category = self.get_category(technology)
        attr = technology.max_diffusion_rate
        attr.set_data(
            default_value=self.DIFFUSION_RATES[category],
            unit="1",
            source=SourceInformation(
                description=(
                    f"The maximum diffusion rate of {technology.name} is set to "
                    f"the historically observed diffusion rate of "
                    f"{self.REFERENCE_TECHNOLOGIES[category]} from Mannhardt "
                    f"et al. (2024)."
                ),
                metadata=self.metadata,
            ),
        )
        return attr
