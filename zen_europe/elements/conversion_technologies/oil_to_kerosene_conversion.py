from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.carrier_availability import CarrierAvailability
from zen_europe.utils.utils import calculate_capacity_addition_from_cumulative, format_capacity_existing

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, SourceInformation


class OilToKeroseneConversion(ConversionTechnology):
    """Class containing all data and assumptions for oil-to-kerosene
    conversion (a refinery output-shifting technology)."""

    name: str = "oil_to_kerosene_conversion"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of oil to kerosene conversion to kerosene.
        """
        return Attribute(
            name="reference_carrier", default_value=["kerosene"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of oil to kerosene conversion to oil.
        """
        return Attribute(name="input_carrier", default_value=["oil"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of oil to kerosene conversion to kerosene.
        """
        return Attribute(
            name="output_carrier", default_value=["kerosene"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of oil to kerosene conversion.

        """
        attr = self.lifetime
        attr.set_data(
            default_value=100,
            source=AssumptionInformation(
                description=(
                    "The lifetime of oil to kerosene conversion is manually "
                    "set to 100 years, effectively representing an "
                    "always-available refinery output-shifting pathway "
                    "rather than a capital asset with a finite technical "
                    "lifetime."
                ),
            ),
        )
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of oil to kerosene conversion.

        Assumed lossless (1 unit of oil converted to 1 unit of kerosene).
        """
        attr = self.conversion_factor
        cf = [{"oil": {"default_value": 1, "unit": "GWh/GWh"}}]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of oil to kerosene conversion "
                    "is manually set to 1, assuming a lossless output shift "
                    "within the refinery product slate."
                ),
            ),
        )
        return attr

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of oil to kerosene conversion.

        """
        attr = self.capacity_existing
        carr_ava = CarrierAvailability(
            source_path=self.source_path,settings=self.settings)
        ex_cap = (carr_ava.get_raw_kerosene_demand(self)).squeeze() 
        ex_cap = ex_cap.to_frame(name=self.settings.time.reference_year - 1)
        ex_cap = calculate_capacity_addition_from_cumulative(ex_cap,element=self)
        ex_cap = format_capacity_existing(ex_cap)
        attr.set_data(
            df=ex_cap,
            source=SourceInformation(
                description=(
                    "The existing capacity of oil to kerosene conversion is "
                    "calculated from the kerosene demand in the reference year." 
                ),
                metadata = carr_ava.metadata
            ),
        )
        return attr
