from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np  

from zen_europe.datasets.dataset_collections.carrier_availability import CarrierAvailability
from zen_europe.datasets.datasets.carrier.ipcc_emission_factors import IPCCEmissionFactors
from zen_europe.datasets.datasets.financial.ECB import ECBInflation,ECBDollar2Euro

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.elements import Carrier
from zen_creator.utils.attribute import Attribute
from zen_europe.datasets.datasets.carrier.bnef import BNEFFuelPrices

class Oil(Carrier):
    """Oil carrier class.

    This class implements the specific behavior for the oil carrier.
    """

    name: str = "oil"
    
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
        Return the import availability of oil.

        """
        if "crude_oil" in self.model.carriers:
            return Attribute(
                    "availability_import",
                    default_value=0,
                    element=self,
                    unit=self.power_unit,
                )
        else:
            if self.settings.availability.cap_oil_import:
                carrier_availability = CarrierAvailability(
                    settings=self.settings, source_path=self.model.source_path)
                return carrier_availability.get_oil_availability(element=self)
            else:
                return Attribute(
                        "availability_import",
                        default_value=np.inf,
                        element=self,
                        unit=self.power_unit,
                    )
    
    def _set_price_import(self) -> Attribute:
        """
        Return the import price of oil.

        """
        if "crude_oil" in self.model.carriers:
            return Attribute(
                    "price_import",
                    default_value=0,
                    element=self,
                    unit="Euro/MWh",
                )
        else:
            bnef_fuel_prices = BNEFFuelPrices(source_path=self.model.source_path)
            return bnef_fuel_prices.get_price_import(element=self)
    
    
    def _set_carbon_intensity_carrier_import(self) -> Attribute:
        """
        Return the carbon intensity of oil.

        """
        if "crude_oil" in self.model.carriers:
            return Attribute(
                    "carbon_intensity_carrier_import",
                    default_value=0,
                    element=self,
                    unit="tCO2/MWh",
                )
        else:
            ipcc_emission_factors = IPCCEmissionFactors(source_path=self.model.source_path)
            return ipcc_emission_factors.get_carbon_intensity(element=self)
