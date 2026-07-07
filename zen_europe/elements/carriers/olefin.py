from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.olefin_demand import OlefinDemand

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute

class Olefin(Carrier):
    """Olefin carrier class.

    This class implements the specific behavior for the olefin carrier.
    """

    name: str = "olefin"
    

    def __init__(self, model: Model, power_unit: str = "tproduct/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ----Example of optional methods for overriding default attributes ------

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of olefin.

        """
        return Attribute(
                "availability_import",
                default_value=0,
                element=self,
                unit=self.power_unit,
            )
    
    def _set_demand(self) -> Attribute:
        """
        Return the demand of olefin.

        """
        olefin_demand = OlefinDemand(
            source_path=self.model.source_path,settings=self.settings)
        return olefin_demand.get_olefin_demand(element=self)