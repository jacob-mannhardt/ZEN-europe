from __future__ import annotations

from pathlib import Path

from zen_creator import Attribute, SourceInformation
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

import pandas as pd

from zen_europe.utils.utils import convert_country_names

class CO2StorageCostsZEP(Dataset[pd.DataFrame]):
    """
    Dataset class for the costs of carbon storage based on the ZEP 
    (Zero Emissions Platform) report.

    """

    name = "co2_storage_costs_zep"
    MONEY_YEAR = 2011

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "The Costs of CO2 Storage: Post-Demonstration CCS in the EU"
            ),
            author=["ZEP", "ieaghg"],
            publication="ZEP",
            publication_year=2011,
            url="https://carbonmanagementeurope.org/publication/the-costs-of-co2-storage/",
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
    def get_lifetime(self) -> Attribute:
        """
        Returns the lifetime from the ZEP carbon storage report.
        """
        return Attribute(
            name="lifetime",
            default_value=40,
            unit="1",
            source=SourceInformation(
                description=(
                    "The lifetime of carbon storage is based on the ZEP report "
                    "'The Costs of CO2 Storage: Post-Demonstration CCS in the EU'."
                    " (Table 4, Case 6, Medium)."
                ),
                metadata=self.metadata,
            )
        )

    def get_opex_specific_variable(self) -> Attribute:
        """
        Returns the specific variable operational expenditure (opex) from the ZEP carbon storage report.
        """
        return Attribute(
            name="opex_specific_variable",
            default_value=4,
            unit="Euro/tCO2",
            source=SourceInformation(
                description=(
                    "The variable opex of carbon storage is based on the ZEP report "
                    "'The Costs of CO2 Storage: Post-Demonstration CCS in the EU'."
                    " (Table 4, Case 6, Medium)."
                ),
                metadata=self.metadata,
            )
        )