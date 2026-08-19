from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class CementKiln(ConversionTechnology):
    """Class containing all data and assumptions for cement kilns (clinker
    production)."""

    name: str = "cement_kiln"

    # tClinker/tCO2eq, https://materialeconomics.com/publications/publication/industrial-transformation-2050
    CLINKER_CARBON_INTENSITY = 0.54

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of cement kilns to clinker.
        """
        return Attribute(
            name="reference_carrier", default_value=["clinker"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of cement kilns to fuel for cement and
        electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["fuel_for_cement", "electricity"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of cement kilns to clinker.
        """
        return Attribute(
            name="output_carrier", default_value=["clinker"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of cement kilns.

        TODO: No lifetime data source has been identified/ported for cement
        kilns; framework default (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of cement kilns.

        Values based on a fuel consumption of 3.7 GJ per ton of clinker
        (AIDRES / Material Economics) and 0.29 GJ of electricity per ton of
        cement, rescaled from cement to clinker basis using the AIDRES
        clinker-to-cement ratio of 0.70.
        """
        attr = self.conversion_factor
        cement_to_clinker = 0.70  # tClinker/tCement, AIDRES
        fuel_consumption_kiln = 3.7  # GJ/ton clinker
        cf = [
            {"electricity": {
                "default_value": 0.29 / 3600 / cement_to_clinker, "unit": "GWh/tonproduct"}},
            {"fuel_for_cement": {
                "default_value": fuel_consumption_kiln / 3600, "unit": "GWh/tonproduct"}},
        ]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of cement kilns is manually "
                    "derived from a fuel consumption of 3.7 GJ per ton of "
                    "clinker (AIDRES / Material Economics) and an "
                    "electricity consumption of 0.29 GJ per ton of cement, "
                    "rescaled to a clinker basis via the AIDRES "
                    "clinker-to-cement ratio of 0.70."
                ),
            ),
        )
        return attr

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        cement kilns.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        attr = self.opex_specific_variable
        attr.set_data(
            default_value=21.5,
            unit="Euro/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The variable opex of cement kilns is manually set to "
                    "21.5 Euro/ton clinker, based on the ECRA (European "
                    "Cement Research Academy) reference plant "
                    "(https://www.ecra-online.org/research/technology-papers, "
                    "Annex II, p. 185)."
                ),
            ),
        )
        return attr

    def _set_carbon_intensity_technology(self) -> Attribute:
        """
        Sets the carbon intensity of cement kilns.

        Returns:
            Attribute: An Attribute object containing the carbon intensity data.
        """
        attr = self.carbon_intensity_technology
        attr.set_data(
            default_value=self.CLINKER_CARBON_INTENSITY,
            unit="ton/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The carbon intensity of cement kilns is manually set "
                    "to the process carbon intensity of clinker production "
                    "(0.54 tCO2/tClinker), based on Material Economics "
                    "(2019), 'Industrial Transformation 2050' "
                    "(https://materialeconomics.com/publications/publication/"
                    "industrial-transformation-2050)."
                ),
            ),
        )
        return attr

    # TODO: capex_specific_conversion/opex_specific_fixed should be sourced
    # from the curated "costs_additional_technologies.xlsx" (AddTech)
    # dataset, which is not yet implemented in zen_europe; framework
    # defaults apply.
