from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.financial.ECB import ECBInflation,ECBDollar2Euro

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute
from zen_europe.datasets.datasets.carrier.bnef import BNEFFuelPrices

class NaturalGas(Carrier):
    """Natural gas carrier class.

    This class implements the specific behavior for the natural gas carrier.
    """

    name: str = "natural_gas"
    
    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)
        # set the inflation rate function from the ECB dataset
        # TODO make the inflation rate function directly available in the model, 
        # so that it can be used by other elements as well
        ecb_inflation = ECBInflation(source_path=self.source_path)
        self.get_inflation_rate = ecb_inflation.get_inflation_rate
        ecb_dollar2euro = ECBDollar2Euro(source_path=self.source_path)
        self.get_dollar2euro = ecb_dollar2euro.get_dollar2euro

    # ----Example of optional methods for overriding default attributes ------

    def _set_availability_import(self) -> Attribute:
        """
        Return the import availability of natural gas.

        """
        return Attribute(
                "availability_import",
                default_value=0,
                element=self,
                unit=self.power_unit,
            )
    
    def _set_price_import(self) -> Attribute:
        """
        Return the import price of natural gas.

        """
        bnef_fuel_prices = BNEFFuelPrices(source_path=self.model.source_path)
        return bnef_fuel_prices.get_price_import(element=self)