from __future__ import annotations

from pathlib import Path

from zen_creator import Attribute, SourceInformation
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

import pandas as pd

from zen_europe.utils.utils import convert_country_names, format_capacity_existing

class IOGPCarbonStorageProjects(Dataset[pd.DataFrame]):
    """
    Dataset class for the existing carbon storage projects based on the IOGP 
    (International Oil & Gas Producers Association) report.

    """

    name = "IOGP_carbon_storage_projects"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "CO2 storage projects in Europe"
            ),
            author=["IOGP"],
            publication="IOGP",
            publication_year=2026,
            url="https://iogpeurope.org/carbon-capture-use-storage-feb2023/",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return (
            Path(self.source_path) / 
            "03-technology" / 
            "capacity_existing" / 
            "carbon_storage" / 
            "co2_storage_projects_europe.csv")

    def _set_data(self) -> pd.DataFrame:
        """ 
        The data is extracted from the IOGP CO2 storage projects database, 
        which is a CSV file containing information about 
        existing carbon storage projects in Europe.

        We allocate all icelandic storage projects to Norway, 
        as we don't have a separate country in the model for Iceland.
        """
        data = pd.read_csv(self.path)
        data["country"] = data["country"].replace({"Iceland": "Norway"})
        data["node"] = convert_country_names(data["country"])
        data = data[data["year_construction"].notna()]
        data = data.set_index(["node","year_construction"])

        return data

    # -------- methods ------------------------    
    def get_capacity_existing(self) -> Attribute:
        """
        Returns the existing carbon storage capacity from the IOGP report.
        """
        data = self.data["co2_storage_injection_capacity_mtpa"]
        data = data/8760*1e6 # convert from Mtpa to tCO2/h
        data = format_capacity_existing(data)
        return Attribute(
            name="capacity_existing",
            default_value=0,
            df=data,
            unit="tCO2/h",
            source=SourceInformation(
                description=(
                    "The existing carbon storage capacity is based on the IOGP report "
                    "'CO2 Storage Projects in Europe'."
                ),
                metadata=self.metadata,
            )
        )

