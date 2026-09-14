from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.hydro_existing_capacity import HydroExistingCapacity
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation, MetaData
from zen_creator.elements import StorageTechnology
from zen_creator.utils.attribute import Attribute, SourceInformation


class ReservoirHydro(StorageTechnology):
    """Class containing all data and assumptions for reservoir hydro storage technology."""

    name: str = "reservoir_hydro"

    ENTSOE_PSR_RESERVOIR = "B12"
    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of reservoir hydro to electricity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Return the lifetime of pumped hydro.

        Currently returns the default value. This method can be
        customized to return a specific lifetime for pumped hydro,
        either as a constant value or as a time series if the lifetime
        varies over time.
        """
        attr = self.lifetime

        return attr.set_data(
            default_value=25,
            source=SourceInformation(
                description="Assumption for default pumped hydro lifetime.",
                metadata=MetaData(
                    name="assumption",
                    title="Modeling assumption",
                    author=["ZEN Europe"],
                    publication="ZEN Europe",
                    publication_year=2026,
                    url=None,
                ),
            ),
        )

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of reservoir hydro.

        The existing hydro capacities are kept if
        settings.investment.keep_existing_hydro_capacities is set, even if
        existing capacities are otherwise not considered.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        if (self.settings.investment.use_existing_capacities
                or self.settings.investment.keep_existing_hydro_capacities):
            hydro_dataset = HydroExistingCapacity(source_path=self.source_path)
            return hydro_dataset.get_capacity_existing(element=self, power=True)
        else:
            attr = self.capacity_existing
            attr.set_data(
                default_value=0,
                df=None,
                source=AssumptionInformation(
                    description=(
                        "We do not consider existing capacities."
                    ),
                ),
            )
            return attr

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of reservoir hydro.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
