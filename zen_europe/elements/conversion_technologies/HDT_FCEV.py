from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, ConversionTechnology


class HDT_FCEV(ConversionTechnology):
    """Class containing all data and assumptions for fuel cell electric
    heavy-duty trucks."""

    name: str = "HDT_FCEV"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of HDT FCEV to truck mileage.
        """
        return Attribute(
            name="reference_carrier", default_value=["truck_mileage"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of HDT FCEV to hydrogen.
        """
        return Attribute(
            name="input_carrier", default_value=["hydrogen"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of HDT FCEV to truck mileage.
        """
        return Attribute(
            name="output_carrier", default_value=["truck_mileage"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of HDT FCEV.

        TODO: No lifetime data source has been identified/ported for HDT
        FCEV; framework default (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of HDT FCEV.

        TODO: Should be sourced from a `HDT_params.xlsx` table (truck
        techno-economic parameters), which is not yet implemented as a
        dataset in zen_europe (see IMPLEMENTATION_TODO.md:
        "VehicleTransportParams" not yet built); left empty.
        """
        attr = self.conversion_factor
        return attr

    # TODO: capacity_existing/max_load should be sourced from truck-fleet/
    # mileage data and the `slp_truck` standard load profile, respectively.
    # capex_specific_conversion/opex_specific_variable should be sourced
    # from `HDT_params.xlsx`. None of these are currently reachable from a
    # clean dataset call for this technology; framework defaults apply
    # throughout.
