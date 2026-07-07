from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator.elements.carriers.carrier import Carrier
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData
from zen_creator.utils.attribute import Attribute, SourceInformation
from zen_europe.utils.utils import convert_country_names, interpolate_missing_years

import pandas as pd

class ShippingTechnologiesKorberg(Dataset[pd.DataFrame]):
    """
    Shipping technologies dataset class from Korberg et al. (2021).

    This class implements the specific behavior for the Shipping Technologies dataset.
    """

    name = "shipping_technologies_korberg"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Techno-economic assessment of advanced fuels and propulsion systems in future fossil-free ships"
            ),
            author=["A.D. Korberg", "S. Brynolf", "M. Grahn", "I.R. Skov"],
            publication="Renewable and Sustainable Energy Reviews",
            publication_year=2021,
            url="https://www.sciencedirect.com/science/article/pii/S1364032121001556",
            doi="https://doi.org/10.1016/j.rser.2021.110861",
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> dict[str, pd.DataFrame]:
        # TODO there is no data to be implemented
        data = {}
        return data

    # -------- methods ------------------------    
    def get_shipping_conversion_factors(self,technology: str) -> dict[str, float]:
        """
        Get the shipping conversion factors for a specific technology.

        This method retrieves the conversion factors for the specified shipping technology
        and returns them as a dictionary.

        Returns:
            A dictionary containing the conversion factors for the specified technology.
        """
        electricity_demand_LH2 = 6.78 # kWh/kg, https://www.sciencedirect.com/science/article/pii/S0306261917305457
        conversion_factors = {
            "diesel_ICE_ship": {"diesel": 1 / 0.45},
            "hydrogen_FC_ship": {"hydrogen":1 / 0.55, 
                                 "electricity": 1 / 0.55 * electricity_demand_LH2}, # alternative fuel mix
            "methanol_ICE_ship": {"methanol": 1 / 0.45},
            "ammonia_ICE_ship": {"ammonia": 1 / 0.45},
        }
        if technology not in conversion_factors:
            raise ValueError(f"Conversion factors for technology" 
                             f"'{technology}' are not available.")
        return conversion_factors[technology]
        