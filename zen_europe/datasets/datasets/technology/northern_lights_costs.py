from __future__ import annotations

from pathlib import Path

from zen_creator import Attribute
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData, SourceInformation

import pandas as pd

from zen_europe.utils.utils import convert_country_names

class NorthernLightsCosts(Dataset[pd.DataFrame]):
    """
    Dataset class for the costs of the Northern Lights Carbon Capture and Storage (CCS) 
    project. This data is based on the external report by Gassnova SF in 2025.

    """

    name = "northern_lights_costs"
    MONEY_YEAR = 2021
    NOK2EURO = 1/10.1633 # Conversion factor from NOK to Euro based on the average exchange rate in 2021.

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Potential for Cost Reductions in the CCS Value Chain"
            ),
            author=["Gassnova SF"],
            publication="Gassnova",
            publication_year=2025,
            url="https://ccsnorway.com/gassnova-fremtidens-ccs-prosjekter-kan-koste-mindre/",
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> dict[str, pd.Series]:
        """ 
        No data to be set
        """
        data = {}
        
        data = pd.Series(data)
        return data

    # -------- methods ------------------------    
    def get_capex_specific(self) -> float:
        """
        Returns the specific CAPEX for the Northern Lights CCS project. 
        We only consider the first phase of the Longship carbon storage facility.
        """
        stored_carbon = 1.5 # mtpa
        capex_permanent_lager = 4.1 # billion NOK
        capex_CO2_terminal = 2.8 # billion NOK
        capex_total = capex_permanent_lager + capex_CO2_terminal # billion NOK
        specific_capex = capex_total / stored_carbon * 8760 # billion NOK per MtCO2/h

        # Convert to Euro
        specific_capex_euro = specific_capex * self.NOK2EURO * 1000 # Euro per tCO2/h

        return specific_capex_euro

    def get_construction_time(self) -> Attribute:
        """
        Returns the construction time of the Northern Lights CCS project. 
        We only consider the first phase of the Longship carbon storage facility.
        https://article23watch.eu/2026/06/19/blog-eu-co2-storage-by-2030-why-the-nzia-target-is-more-feasible-than-industry-claims/
        """
        return Attribute(
            name="construction_time",
            default_value=4,
            unit="1",
            source=SourceInformation(
                description=(
                    "The construction time of carbon storage is based on the Longship "
                    "carbon storage facility, which is part of the Northern Lights CCS project. "
                ),
                metadata=self.metadata,
            )
        )