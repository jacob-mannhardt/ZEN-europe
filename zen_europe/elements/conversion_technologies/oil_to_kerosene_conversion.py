from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


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

        TODO: No lifetime data source has been identified/ported for this
        technology (the legacy pipeline also leaves it at the framework
        default); framework default (NaN) is kept.
        """
        attr = self.lifetime
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

    # TODO: capacity_existing should be sourced from kerosene demand
    # (cd.kerosene_demand in the legacy pipeline); no equivalent hook is
    # available yet in zen_europe, so the framework default (0) applies.
