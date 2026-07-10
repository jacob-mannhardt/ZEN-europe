from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model
from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute
from zen_europe.datasets.datasets.carrier.ifa import IFA

class Ammonia(Carrier):
    """Ammonia carrier class.

    This class implements the specific behavior for the ammonia carrier.
    """

    name: str = "ammonia"
    

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)
        # GWh per ton NH3, Danish Energy Agency "Technology Data for Renewable Fuels"
        # https://ens.dk/en/analyses-and-statistics/technology-data-renewable-fuels
        self._TON_NH3_TO_GWH = 18.9 / 3600

    # ----Example of optional methods for overriding default attributes ------

    def _set_demand(self) -> Attribute:
        """
        Return the demand of ammonia.

        """
        ifa = IFA(source_path=self.source_path)
        return ifa.get_demand(element=self)

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of ammonia.

        """
        return Attribute(
                "availability_import",
                default_value=0,
                element=self,
                unit=self.power_unit,
            )