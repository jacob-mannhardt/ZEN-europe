from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.technology.tyndp_scenario_building_guidelines import (
    TYNDPScenarioBuildingGuidelines,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation
from zen_creator.elements import TransportTechnology
from zen_creator.utils.attribute import Attribute


class OilPipeline(TransportTechnology):
    """Class containing all data and assumptions for oil pipeline transport
    technology."""

    name: str = "oil_pipeline"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of oil pipeline to oil.
        """
        return Attribute(
            name="reference_carrier", default_value=["oil"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of oil pipeline.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=60,
            source=AssumptionInformation(
                description=(
                    "The lifetime of oil pipelines is manually set to 60 "
                    "years, in line with the lifetime of the other linear "
                    "transport infrastructure."
                ),
            ),
        )

    def _set_transport_loss_factor_linear(self) -> Attribute:
        """
        Sets the linear transport loss factor of oil pipeline.
        """
        attr = self.transport_loss_factor_linear
        return attr.set_data(
            default_value=5e-5,
            unit="1/km",
            source=AssumptionInformation(
                description=(
                    "The transport losses of oil pipelines are manually set "
                    "to 5e-5 per km, in line with the losses of the other "
                    "linear transport infrastructure."
                ),
            ),
        )

    def _set_capex_per_distance_transport(self) -> Attribute:
        """
        Sets the distance-specific capex of oil pipeline.

        The investment cost is assumed to equal the investment cost of natural
        gas pipelines.
        """
        pipeline_costs = TYNDPScenarioBuildingGuidelines(
            source_path=self.source_path)
        return pipeline_costs.get_capex_per_distance_transport(self)
