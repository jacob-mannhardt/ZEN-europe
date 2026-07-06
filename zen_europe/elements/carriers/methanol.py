from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute
from zen_europe.datasets.dataset_collections.methanol_demand import MethanolDemand

class Methanol(Carrier):
    """Methanol carrier class.

    This class implements the specific behavior for the methanol carrier.
    """

    name: str = "methanol"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ----Example of optional methods for overriding default attributes ------

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of methanol.

        """
        return Attribute(
                "availability_import",
                default_value=0,
                element=self,
                unit=self.power_unit,
            )
    
    def _set_demand(self) -> Attribute:
        """
        Return the demand of methanol.

        """
        methanol_demand = MethanolDemand(source_path=self.model.source_path)
        return methanol_demand.get_methanol_demand(element=self)