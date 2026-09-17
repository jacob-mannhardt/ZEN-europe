from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

from zen_creator import Attribute, SourceInformation, TransportTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData


class DEACarbonTransport(Dataset[pd.DataFrame]):
    """
    CO2 transport dataset class from the technology catalogue for carbon
    capture, transport and storage of the Danish Energy Agency.

    Provides the lifetime of CO2 pipelines, read from the CO2 transport data
    sheets of the catalogue.
    """

    name = "dea_carbon_transport"

    LIFETIMES = {
        "carbon_pipeline": 50,
    }

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Technology Data for Carbon Capture, Transport and Storage",
            author=["Danish Energy Agency"],
            publication="Danish Energy Agency",
            publication_year=2026,
            url=(
                "https://ens.dk/en/analyses-and-statistics/"
                "technology-data-carbon-capture-transport-and-storage"
            ),
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> dict[str, pd.DataFrame]:
        """
        No data to be set.
        """
        data: dict[str, pd.DataFrame] = {}
        return data

    # -------- methods ------------------------
    def get_lifetime(self, technology: TransportTechnology) -> Attribute:
        """
        Get the lifetime of a transport technology.
        """
        if technology.name not in self.LIFETIMES:
            raise ValueError(
                f"The lifetime of technology '{technology.name}' is not "
                f"available in the dataset '{self.name}'."
            )
        attr = technology.lifetime
        return attr.set_data(
            default_value=self.LIFETIMES[technology.name],
            source=SourceInformation(
                description=(
                    f"The lifetime of {technology.name} is based on the CO2 "
                    "transport data of the carbon capture, transport and "
                    "storage catalogue of the Danish Energy Agency."
                ),
                metadata=self.metadata,
            ),
        )
