from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class OilToGasolineConversion(ConversionTechnology):
    """Class containing all data and assumptions for oil-to-gasoline
    conversion (a refinery output-shifting technology)."""

    name: str = "oil_to_gasoline_conversion"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of oil to gasoline conversion to gasoline.
        """
        return Attribute(
            name="reference_carrier", default_value=["gasoline"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of oil to gasoline conversion to oil.
        """
        return Attribute(name="input_carrier", default_value=["oil"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of oil to gasoline conversion to gasoline.
        """
        return Attribute(
            name="output_carrier", default_value=["gasoline"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of oil to gasoline conversion.

        """
        attr = self.lifetime
        attr.set_data(
            default_value=100,
            source=AssumptionInformation(
                description=(
                    "The lifetime of oil to gasoline conversion is "
                    "manually set to 100 years, effectively representing "
                    "an always-available refinery output-shifting "
                    "pathway rather than a capital asset with a finite "
                    "technical lifetime."
                ),
            ),
        )
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of oil to gasoline conversion.

        Assumed lossless (1 unit of oil converted to 1 unit of gasoline).
        """
        attr = self.conversion_factor
        cf = [{"oil": {"default_value": 1, "unit": "GWh/GWh"}}]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of oil to gasoline conversion "
                    "is manually set to 1, assuming a lossless output shift "
                    "within the refinery product slate."
                ),
            ),
        )
        return attr

    # TODO: opex_specific_variable should be sourced from the price delta
    # between gasoline and oil (BNEF fuel price data), conditional on the
    # `assume_oil_price_for_diesel_and_gasoline` scenario flag in the legacy
    # pipeline. A BNEF fuel-price dataset exists in zen_europe
    # (zen_europe/datasets/datasets/carrier/bnef_fuelprices.py), but wiring
    # up the conditional price-delta logic is left as a TODO; framework
    # default (0) applies.
