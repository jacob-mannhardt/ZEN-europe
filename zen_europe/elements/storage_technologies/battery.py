from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import (
    AssumptionInformation,
    MetaData,
)
from zen_creator.elements import StorageTechnology
from zen_creator.utils.attribute import Attribute, SourceInformation

# Battery lifetime, round-trip efficiency and construction time are taken from
# the electricity storage review of Schmidt et al. (2019).
SCHMIDT_STORAGE = MetaData(
    name="storage_schmidt",
    title=(
        "Projecting the Future Levelized Cost of Electricity Storage "
        "Technologies"
    ),
    author=["Oliver Schmidt", "Sylvain Melchior", "Adam Hawkes", "Iain Staffell"],
    publication="Joule",
    publication_year=2019,
    doi="https://doi.org/10.1016/j.joule.2018.12.008",
)

# The energy-to-power ratio of utility-scale batteries follows the reference
# storage duration of the NREL Annual Technology Baseline.
NREL_ATB = MetaData(
    name="nrel_atb_battery",
    title="2023 Annual Technology Baseline: Utility-Scale Battery Storage",
    author=["National Renewable Energy Laboratory"],
    publication="National Renewable Energy Laboratory",
    publication_year=2023,
    url="https://atb.nrel.gov/electricity/2023/utility-scale_battery_storage",
)


class Battery(StorageTechnology):
    """Class containing all data and assumptions for battery storage technology."""

    name: str = "battery"

    # round-trip efficiency, split evenly between charging and discharging
    EFFICIENCY_ROUND_TRIP = 0.86
    # energy-to-power ratio of a utility-scale battery, in hours
    ENERGY_TO_POWER_RATIO = 4

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of battery to electricity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of battery.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=13,
            source=SourceInformation(
                description=(
                    "The lifetime of battery storage is based on the "
                    "lithium-ion battery of Schmidt et al. (2019)."
                ),
                metadata=SCHMIDT_STORAGE,
            ),
        )

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of battery.
        """
        if not self.settings.investment.use_construction_times:
            return self.construction_time
        attr = self.construction_time
        return attr.set_data(
            default_value=1,
            source=SourceInformation(
                description=(
                    "The construction time of battery storage is based on the "
                    "lithium-ion battery of Schmidt et al. (2019)."
                ),
                metadata=SCHMIDT_STORAGE,
            ),
        )

    def _set_efficiency_charge(self) -> Attribute:
        """
        Sets the charging efficiency of battery.
        """
        attr = self.efficiency_charge
        return attr.set_data(
            default_value=np.sqrt(self.EFFICIENCY_ROUND_TRIP),
            source=SourceInformation(
                description=(
                    "The round-trip efficiency of battery storage is "
                    f"{self.EFFICIENCY_ROUND_TRIP} (lithium-ion battery of "
                    "Schmidt et al. (2019)) and is split evenly between "
                    "charging and discharging."
                ),
                metadata=SCHMIDT_STORAGE,
            ),
        )

    def _set_efficiency_discharge(self) -> Attribute:
        """
        Sets the discharging efficiency of battery.
        """
        attr = self.efficiency_discharge
        return attr.set_data(
            default_value=np.sqrt(self.EFFICIENCY_ROUND_TRIP),
            source=SourceInformation(
                description=(
                    "The round-trip efficiency of battery storage is "
                    f"{self.EFFICIENCY_ROUND_TRIP} (lithium-ion battery of "
                    "Schmidt et al. (2019)) and is split evenly between "
                    "charging and discharging."
                ),
                metadata=SCHMIDT_STORAGE,
            ),
        )

    def _set_self_discharge(self) -> Attribute:
        """
        Sets the self-discharge of battery.
        """
        attr = self.self_discharge
        return attr.set_data(
            default_value=0.001,
            source=AssumptionInformation(
                description=(
                    "The self-discharge of battery storage is manually set to "
                    "0.1% of the stored energy per hour."
                ),
            ),
        )

    def _set_energy_to_power_ratio_min(self) -> Attribute:
        """
        Sets the minimum energy-to-power ratio of battery.
        """
        if not self.settings.investment.use_battery_e2p_ratio:
            return self.energy_to_power_ratio_min
        attr = self.energy_to_power_ratio_min
        return attr.set_data(
            default_value=self.ENERGY_TO_POWER_RATIO,
            source=SourceInformation(
                description=(
                    "The energy-to-power ratio of battery storage is fixed to "
                    f"{self.ENERGY_TO_POWER_RATIO} hours, the reference "
                    "duration of utility-scale battery storage in the NREL "
                    "Annual Technology Baseline."
                ),
                metadata=NREL_ATB,
            ),
        )

    def _set_energy_to_power_ratio_max(self) -> Attribute:
        """
        Sets the maximum energy-to-power ratio of battery.
        """
        if not self.settings.investment.use_battery_e2p_ratio:
            return self.energy_to_power_ratio_max
        attr = self.energy_to_power_ratio_max
        return attr.set_data(
            default_value=self.ENERGY_TO_POWER_RATIO,
            source=SourceInformation(
                description=(
                    "The energy-to-power ratio of battery storage is fixed to "
                    f"{self.ENERGY_TO_POWER_RATIO} hours, the reference "
                    "duration of utility-scale battery storage in the NREL "
                    "Annual Technology Baseline."
                ),
                metadata=NREL_ATB,
            ),
        )

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of battery.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)

