from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class BiomassToCementFuel(ConversionTechnology):
    """Class containing all data and assumptions for biomass-fired
    cement-kiln fuel supply (biomass to fuel for cement)."""

    name: str = "biomass_to_cement_fuel"

    # GJ/ton hard-coal-equivalent fuel-for-cement reference, AIDRES p. 51,
    # https://op.europa.eu/en/publication-detail/-/publication/577d820d-5115-11ee-9220-01aa75ed71a1/language-en
    CONSUMPTION_HARD_COAL = 2.13

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of biomass to cement fuel to fuel for
        cement.
        """
        return Attribute(
            name="reference_carrier", default_value=["fuel_for_cement"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of biomass to cement fuel to biomass.
        """
        return Attribute(
            name="input_carrier", default_value=["biomass"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of biomass to cement fuel to fuel for cement.
        """
        return Attribute(
            name="output_carrier", default_value=["fuel_for_cement"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of biomass to cement fuel.

        TODO: No lifetime data source has been identified/ported for this
        technology; framework default (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of biomass to cement fuel.

        Value based on a fuel energy content of 2.77 GJ/ton for biomass,
        relative to the 2.13 GJ/ton hard-coal-equivalent fuel-for-cement
        reference (AIDRES p. 51).
        """
        attr = self.conversion_factor
        cf = [{"biomass": {
            "default_value": 2.77 / self.CONSUMPTION_HARD_COAL, "unit": "GWh/GWh"}}]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of biomass to cement fuel is "
                    "manually derived from a fuel energy content of "
                    "2.77 GJ/ton for biomass, relative to the 2.13 GJ/ton "
                    "hard-coal-equivalent fuel-for-cement reference "
                    "(AIDRES, p. 51)."
                ),
            ),
        )
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for biomass to cement
        fuel.

        Based on ECRA (2022), Technology Paper 14,
        https://ecra-online.org/fileadmin/redaktion/files/pdf/ECRA_Technology_Papers_2022.pdf.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        attr = self.capex_specific_conversion
        capex = _get_capex_cement_fuel_retrofit(additional_cost=15 * 1e6)
        attr.set_data(
            default_value=capex,
            unit="Euro/GW",
            source=AssumptionInformation(
                description=(
                    "The specific capex of biomass to cement fuel is "
                    "manually derived from the ECRA (European Cement "
                    "Research Academy) reference-plant retrofit cost of "
                    "320 M EUR for a 2 Mt/a clinker plant, plus an "
                    "additional 15 M EUR retrofitting cost for biomass "
                    "firing (assuming the upper end of the cost range, to "
                    "account for the difficulties with high substitution "
                    "rates), based on "
                    "https://ecra-online.org/fileadmin/redaktion/files/pdf/"
                    "ECRA_Technology_Papers_2022.pdf, Technology Paper 14."
                ),
            ),
        )
        return attr

    # TODO: capacity_existing should be sourced from clinker demand times the
    # existing kiln fuel-consumption and biomass fuel share
    # (`_existing_capacity_cement_fuel` in the legacy pipeline, using a 16%
    # existing biomass share from AIDRES); no clean equivalent hook is
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
