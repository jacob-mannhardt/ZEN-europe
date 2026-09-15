from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import MetaData
from zen_creator.elements import StorageTechnology
from zen_creator.utils.attribute import Attribute, SourceInformation

# Lifetime and round-trip efficiency of hydrogen storage caverns are taken from
# the energy storage catalogue of the Danish Energy Agency.
DEA_ENERGY_STORAGE = MetaData(
    name="dea_energy_storage",
    title="Technology Data for Energy Storage",
    author=["Danish Energy Agency"],
    publication="Danish Energy Agency",
    publication_year=2026,
    url=(
        "https://ens.dk/en/our-services/technology-catalogues/"
        "technology-data-energy-storage"
    ),
    note="Hydrogen storage caverns, assuming pre-existing salt caverns.",
)


class SaltCavernStorage(StorageTechnology):
    """Class containing all data and assumptions for hydrogen salt cavern
    storage technology."""

    name: str = "salt_cavern_storage"

    # round-trip efficiency, split evenly between charging and discharging
    EFFICIENCY_ROUND_TRIP = 0.99

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of salt cavern storage to hydrogen.
        """
        return Attribute(
            name="reference_carrier", default_value=["hydrogen"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of salt cavern storage.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=100,
            source=SourceInformation(
                description=(
                    "The lifetime of hydrogen storage caverns is based on the "
                    "energy storage catalogue of the Danish Energy Agency. "
                    "The caverns are assumed to exist already, so they do not "
                    "retire within the modeling horizon."
                ),
                metadata=DEA_ENERGY_STORAGE,
            ),
        )

    def _set_efficiency_charge(self) -> Attribute:
        """
        Sets the charging efficiency of salt cavern storage.
        """
        attr = self.efficiency_charge
        return attr.set_data(
            default_value=np.sqrt(self.EFFICIENCY_ROUND_TRIP),
            source=SourceInformation(
                description=(
                    "The round-trip efficiency of hydrogen storage caverns is "
                    f"{self.EFFICIENCY_ROUND_TRIP} (energy storage catalogue "
                    "of the Danish Energy Agency) and is split evenly between "
                    "charging and discharging."
                ),
                metadata=DEA_ENERGY_STORAGE,
            ),
        )

    def _set_efficiency_discharge(self) -> Attribute:
        """
        Sets the discharging efficiency of salt cavern storage.
        """
        attr = self.efficiency_discharge
        return attr.set_data(
            default_value=np.sqrt(self.EFFICIENCY_ROUND_TRIP),
            source=SourceInformation(
                description=(
                    "The round-trip efficiency of hydrogen storage caverns is "
                    f"{self.EFFICIENCY_ROUND_TRIP} (energy storage catalogue "
                    "of the Danish Energy Agency) and is split evenly between "
                    "charging and discharging."
                ),
                metadata=DEA_ENERGY_STORAGE,
            ),
        )
