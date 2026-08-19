from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, ConversionTechnology


class BEV(ConversionTechnology):
    """Class containing all data and assumptions for battery electric
    vehicles (BEV, passenger transport)."""

    name: str = "BEV"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of BEV to passenger mileage.
        """
        return Attribute(
            name="reference_carrier", default_value=["passenger_mileage"],
            element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of BEV to electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["electricity"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of BEV to passenger mileage.
        """
        return Attribute(
            name="output_carrier", default_value=["passenger_mileage"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of BEV.

        TODO: No lifetime data source has been identified/ported for BEV
        (the legacy pipeline's `get_transport_constants("lifetime")=20` is
        dead/commented-out code); framework default (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of BEV.

        TODO: Should be sourced from a `vehicle_tech_parameters.csv` table
        (passenger-vehicle techno-economic parameters), which is not yet
        implemented as a dataset in zen_europe (see IMPLEMENTATION_TODO.md:
        "VehicleTransportParams" not yet built); left empty.
        """
        attr = self.conversion_factor
        return attr

    # TODO: capacity_existing/max_load should be sourced from Eurostat
    # vehicle-stock/mileage data and the `slp_passenger` standard load
    # profile, respectively. capex_specific_conversion/opex_specific_variable
    # should be sourced from `vehicle_tech_parameters.csv`. None of these are
    # currently reachable from a clean dataset call for this technology;
    # framework defaults apply throughout.
