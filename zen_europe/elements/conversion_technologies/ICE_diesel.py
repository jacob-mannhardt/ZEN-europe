from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, ConversionTechnology


class ICE_diesel(ConversionTechnology):
    """Class containing all data and assumptions for diesel internal
    combustion engine passenger vehicles."""

    name: str = "ICE_diesel"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of ICE diesel to passenger mileage.
        """
        return Attribute(
            name="reference_carrier", default_value=["passenger_mileage"],
            element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of ICE diesel to diesel.
        """
        return Attribute(name="input_carrier", default_value=["diesel"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of ICE diesel to passenger mileage.
        """
        return Attribute(
            name="output_carrier", default_value=["passenger_mileage"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of ICE diesel.

        TODO: No lifetime data source has been identified/ported for ICE
        diesel; framework default (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of ICE diesel.

        TODO: Should be sourced from a `vehicle_tech_parameters.csv` table
        (passenger-vehicle techno-economic parameters), which is not yet
        implemented as a dataset in zen_europe (see IMPLEMENTATION_TODO.md:
        "VehicleTransportParams" not yet built); left empty.
        """
        attr = self.conversion_factor
        return attr

    # TODO: capacity_existing/capacity_limit/max_load should be sourced from
    # Eurostat vehicle-stock data, an ICE phase-out year (under the
    # `force_ice_phase_out` scenario flag), and the `slp_passenger` standard
    # load profile, respectively. capex_specific_conversion/
    # opex_specific_variable should be sourced from
    # `vehicle_tech_parameters.csv`. None of these are currently reachable
    # from a clean dataset call for this technology; framework defaults
    # apply throughout.
