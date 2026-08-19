from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class H2_DRI(ConversionTechnology):
    """Class containing all data and assumptions for hydrogen-based direct
    reduced iron (H2-DRI) primary steelmaking."""

    name: str = "H2_DRI"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of H2-DRI to primary steel.
        """
        return Attribute(
            name="reference_carrier", default_value=["primary_steel"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of H2-DRI to hydrogen, electricity and hard
        coal.
        """
        return Attribute(
            name="input_carrier",
            default_value=["hydrogen", "electricity", "hard_coal"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of H2-DRI to primary steel.
        """
        return Attribute(
            name="output_carrier", default_value=["primary_steel"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of H2-DRI.

        TODO: No lifetime data source has been identified/ported for H2-DRI
        (the legacy pipeline has the same open TODO); framework default
        (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of H2-DRI.

        Values based on Agora Industry (2021), 'Low-carbon technologies for
        the global steel transformation': 8.25 GJ hydrogen, 2.06 GJ
        electricity (DRI + EAF) and 0.53 GJ hard coal (electrode/additives)
        per ton of primary steel.
        https://www.agora-industry.org/publications/low-carbon-technologies-for-the-global-steel-transformation
        """
        attr = self.conversion_factor
        cf = [
            {"hydrogen": {"default_value": 8.25 / 3600, "unit": "GWh/tonproduct"}},
            {"electricity": {
                "default_value": (0.29 + 1.77) / 3600, "unit": "GWh/tonproduct"}},
            {"hard_coal": {"default_value": 0.53 / 3600, "unit": "GWh/tonproduct"}},
        ]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of H2-DRI is manually derived "
                    "from Agora Industry (2021), 'Low-carbon technologies "
                    "for the global steel transformation'."
                ),
            ),
        )
        return attr

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        H2-DRI.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        attr = self.opex_specific_variable
        attr.set_data(
            default_value=340.2646,
            unit="Euro/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The variable opex of H2-DRI is manually set based on "
                    "Agora Industry (2021), 'Low-carbon technologies for "
                    "the global steel transformation'."
                ),
            ),
        )
        return attr

    def _set_carbon_intensity_technology(self) -> Attribute:
        """
        Sets the carbon intensity of H2-DRI.

        Returns:
            Attribute: An Attribute object containing the carbon intensity data.
        """
        attr = self.carbon_intensity_technology
        attr.set_data(
            default_value=0.01,
            unit="ton/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The carbon intensity of H2-DRI is manually set based "
                    "on Agora Industry (2021), 'Low-carbon technologies for "
                    "the global steel transformation', representing "
                    "residual process emissions not attributable to the "
                    "hard_coal carrier's carbon intensity."
                ),
            ),
        )
        return attr

    # TODO: capex_specific_conversion/opex_specific_fixed should be sourced
    # from the curated "costs_additional_technologies.xlsx" (AddTech)
    # dataset, which is not yet implemented in zen_europe; framework
    # defaults apply.

    # TODO: capacity_existing has no ported data source for H2-DRI (legacy
    # pipeline also leaves it at 0); framework default applies.
