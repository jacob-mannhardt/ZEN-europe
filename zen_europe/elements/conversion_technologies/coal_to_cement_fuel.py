from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class CoalToCementFuel(ConversionTechnology):
    """Class containing all data and assumptions for coal-fired cement-kiln
    fuel supply (hard coal to fuel for cement)."""

    name: str = "coal_to_cement_fuel"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of coal to cement fuel to fuel for cement.
        """
        return Attribute(
            name="reference_carrier", default_value=["fuel_for_cement"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of coal to cement fuel to hard coal.
        """
        return Attribute(
            name="input_carrier", default_value=["hard_coal"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of coal to cement fuel to fuel for cement.
        """
        return Attribute(
            name="output_carrier", default_value=["fuel_for_cement"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of coal to cement fuel.

        TODO: No lifetime data source has been identified/ported for this
        technology; framework default (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of coal to cement fuel.

        Hard coal is the fuel-for-cement reference fuel, so the conversion
        factor is 1.
        """
        attr = self.conversion_factor
        cf = [{"hard_coal": {"default_value": 1, "unit": "GWh/GWh"}}]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of coal to cement fuel is "
                    "manually set to 1, since hard coal is used as the "
                    "reference fuel for the cement-fuel-for-cement carrier."
                ),
            ),
        )
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for coal to cement fuel.

        Based on ECRA (2022), Technology Paper 14 ff.,
        https://ecra-online.org/fileadmin/redaktion/files/pdf/ECRA_Technology_Papers_2022.pdf.
        No retrofitting is needed for coal-fired kilns (no additional
        investment on top of the standard reference-plant cost).

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        attr = self.capex_specific_conversion
        capex = _get_capex_cement_fuel_retrofit(additional_cost=0)
        attr.set_data(
            default_value=capex,
            unit="Euro/GW",
            source=AssumptionInformation(
                description=(
                    "The specific capex of coal to cement fuel is manually "
                    "derived from the ECRA (European Cement Research "
                    "Academy) reference-plant retrofit cost of 320 M EUR "
                    "for a 2 Mt/a clinker plant, with no additional "
                    "retrofitting cost for coal firing "
                    "(https://ecra-online.org/fileadmin/redaktion/files/pdf/"
                    "ECRA_Technology_Papers_2022.pdf, Technology Paper 14)."
                ),
            ),
        )
        return attr

    # TODO: capacity_existing should be sourced from the existing share of
    # coal-fired cement-fuel capacity within total clinker demand
    # (`_existing_capacity_cement_fuel` in the legacy pipeline, using a 54%
    # existing coal share from AIDRES); no clean equivalent hook is
    # available yet in zen_europe, so the framework default (0) applies.


def _get_capex_cement_fuel_retrofit(additional_cost: float) -> float:
    """Specific capex [Euro/GW] for retrofitting a cement kiln to a
    different fuel-for-cement fuel.

    Based on ECRA (2022), Technology Paper 14 ff. The reference plant costs
    320 M EUR for a 2 Mt/a clinker plant (Annex II, p. 185); ``additional_cost``
    adds the fuel-specific retrofitting investment on top of that reference
    cost.
    """
    standard_cost = 320 * 1e6  # Euro, for 2 Mt/a clinker
    size_ton_per_h = 2 * 1e6 / 8760  # ton clinker/h
    fuel_consumption_kiln = 3.7  # GJ/ton clinker
    clinker_to_fuel = fuel_consumption_kiln / 3600  # GWh/ton clinker
    size_gw = size_ton_per_h * clinker_to_fuel
    return (standard_cost + additional_cost) / size_gw
