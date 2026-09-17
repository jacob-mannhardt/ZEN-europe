from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

from zen_creator import Attribute, SourceInformation, TransportTechnology
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData


class DEAEnergyTransport(Dataset[pd.DataFrame]):
    """
    Energy transport dataset class from the technology catalogue for energy
    transport of the Danish Energy Agency.

    Provides the lifetime and the transport losses of hydrogen pipelines, read
    from the data sheet of the main hydrogen distribution line (70 bar).
    """

    name = "dea_energy_transport"

    LIFETIMES = {
        "hydrogen_pipeline": 50,
    }
    # transport losses per 1000 km, converted to losses per km in the getter
    TRANSPORT_LOSSES_PER_1000_KM = {
        "hydrogen_pipeline": 0.029,
    }

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Technology Data for Energy Transport",
            author=["Danish Energy Agency"],
            publication="Danish Energy Agency",
            publication_year=2026,
            url=(
                "https://ens.dk/en/our-services/technology-catalogues/"
                "technology-data-energy-transport"
            ),
            note="Main distribution line, hydrogen, 70 bar.",
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
                    f"The lifetime of {technology.name} is based on the main "
                    "distribution line (70 bar) of the energy transport "
                    "catalogue of the Danish Energy Agency."
                ),
                metadata=self.metadata,
            ),
        )

    def get_transport_loss_factor_linear(
            self, technology: TransportTechnology) -> Attribute:
        """
        Get the linear transport loss factor of a transport technology.
        """
        if technology.name not in self.TRANSPORT_LOSSES_PER_1000_KM:
            raise ValueError(
                f"The transport losses of technology '{technology.name}' are "
                f"not available in the dataset '{self.name}'."
            )
        transport_losses = self.TRANSPORT_LOSSES_PER_1000_KM[technology.name]
        attr = technology.transport_loss_factor_linear
        return attr.set_data(
            default_value=transport_losses / 1000,
            unit="1/km",
            source=SourceInformation(
                description=(
                    f"The transport losses of {technology.name} are "
                    f"{transport_losses:.1%} per 1000 km, based on the main "
                    "distribution line (70 bar) of the energy transport "
                    "catalogue of the Danish Energy Agency."
                ),
                metadata=self.metadata,
            ),
        )
