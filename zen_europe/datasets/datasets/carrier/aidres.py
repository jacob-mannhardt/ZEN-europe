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

class Aidres(Dataset[pd.DataFrame]):
    """
    Aidres dataset class.

    This class implements the specific behavior for the Aidres dataset.
    """

    name = "aidres"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Advancing industrial decarbonisation by assessing the "
                "future use of renewable energies in industrial processes"
            ),
            author=["Luc Girardin",
                    "Juan Correa Laguna",
                    "Joris Valee"],
            publication="Publications Office of the European Union",
            publication_year=2023,
            url="https://data.europa.eu/doi/10.2833/696697",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path / "02-carrier" / "industry" 

    def _set_data(self) -> dict[str, pd.DataFrame]:
        prod_flow = pd.read_excel(self.path / "AIDRES_demand_database.xlsx",
                sheet_name="Product Flow", header=12).set_index("NUTS ID")
        cement_demand = prod_flow["Cement (kt/y)"]
        steel_demand = prod_flow["Steel (kt/y)"]
        methanol_demand = pd.read_excel(self.path / "AIDRES_demand_database.xlsx",
                sheet_name="Methanol (PJ per y)", header=12).set_index("NUTS ID")
        methanol_demand = methanol_demand["All sectors (PJ/y).1"]

        data = {
            "cement": cement_demand.to_frame(name="demand"),
            "steel": steel_demand.to_frame(name="demand"),
            "methanol": methanol_demand.to_frame(name="demand")
        }
        return data

    # -------- methods ------------------------
    def get_demand(self, element: Carrier) -> pd.DataFrame:
        """
        Get the demand of cement, steel, or methanol from the Aidres dataset.

        This method retrieves the demand data for the 
        specified carrier from the Aidres dataset
        and returns it as a pandas DataFrame.

        Args:
            element (Carrier): The carrier element for which to get the demand.

        Returns:
            A pandas DataFrame containing the demand data for the specified carrier.
        """
        data = self.data[element.name]
        common_countries = pd.Index(data.index).intersection(
            element.model.config.system.set_nodes)
        data = data.loc[common_countries]
        return data
    
    def get_CEM2_clinker_ratio(self) -> float:
        """
        Get the clinker to cement ratio from the Aidres dataset.

        This method retrieves the clinker to cement ratio from the Aidres dataset
        and returns it as a float.

        Returns:
            A float representing the clinker to cement ratio.
        """
        return 0.7
        