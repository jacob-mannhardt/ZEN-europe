from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.financial.ECB import ECBDollar2Euro

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, SourceInformation


class Refining(ConversionTechnology):
    """Class containing all data and assumptions for oil refining
    (crude oil and hydrogen to oil products)."""

    name: str = "refining"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of refining to oil.
        """
        return Attribute(
            name="reference_carrier", default_value=["oil"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of refining to crude oil and hydrogen.
        """
        return Attribute(
            name="input_carrier", default_value=["crude_oil", "hydrogen"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of refining to oil.
        """
        return Attribute(
            name="output_carrier", default_value=["oil"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of refining.

        """
        attr = self.lifetime
        attr.set_data(
            default_value=30,
            source=AssumptionInformation(
                description=(
                    "The lifetime of refining is manually set to 30 years, "
                    "based on https://www.mdpi.com/1996-1073/12/24/4664."
                ),
            ),
        )
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of refining.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            attr.set_data(
                default_value=3,
                source=AssumptionInformation(
                    description=(
                        "The construction time of refining is manually set "
                        "to 3 years, based on "
                        "https://www.mdpi.com/1996-1073/12/24/4664."
                    ),
                ),
            )
            return attr
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of refining.

        Hydrogen demand for hydrotreating/hydrocracking is manually set to
        0.541 MWh_H2/toe of oil product, converted to a MWh/MWh basis using
        the standard MWh-to-toe conversion factor (1 MWh = 0.0859845 toe).
        """
        attr = self.conversion_factor
        mwh_to_toe = 0.0859845
        cf = [
            {"crude_oil": {"default_value": 1, "unit": "GWh/GWh"}},
            {"hydrogen": {
                "default_value": 0.541 * mwh_to_toe, "unit": "GWh/GWh"}},
        ]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of refining is manually set, "
                    "assuming a lossless crude-oil-to-oil conversion and a "
                    "hydrogen demand of 0.541 MWh H2 per toe of oil product."
                ),
            ),
        )
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for refining.

        Manually set based on an investment of 6 bn USD for an 8 Mt/y
        refinery, https://link.springer.com/chapter/10.1007/978-3-030-86884-0_3

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        attr = self.capex_specific_conversion
        ecb_dataset = ECBDollar2Euro(source_path=self.source_path)
        dollar2euro = ecb_dataset.get_dollar2euro(2022)
        mwh_to_toe = 0.0859845
        capacity_mt_per_h = 8 / 8760
        capex = 6 * 1e3 / capacity_mt_per_h * dollar2euro * mwh_to_toe
        attr.set_data(
            default_value=capex,
            unit="Euro/MW",
            source=SourceInformation(
                description=(
                    "The specific capex of refining is a manually derived "
                    "value assuming an investment of 6 bn USD for an 8 Mt/y "
                    "refinery, converted to EUR using the ECB USD/EUR "
                    "reference exchange rate for 2022."
                ),
                metadata=ecb_dataset.metadata,
            ),
        )
        return attr

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for refining.

        Manually set assuming 1.5% of investment for maintenance plus
        27.5 M USD/year for personnel (midpoint of the 15-40 M USD/year
        range), https://link.springer.com/chapter/10.1007/978-3-030-86884-0_3

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        attr = self.opex_specific_fixed
        ecb_dataset = ECBDollar2Euro(source_path=self.source_path)
        dollar2euro = ecb_dataset.get_dollar2euro(2022)
        mwh_to_toe = 0.0859845
        capacity_mt_per_h = 8 / 8760
        opex_fixed = (
            (0.015 * 6 * 1e3 + 27.5) / capacity_mt_per_h * dollar2euro * mwh_to_toe)
        attr.set_data(
            default_value=opex_fixed,
            unit="Euro/MW",
            source=SourceInformation(
                description=(
                    "The specific fixed opex of refining is a manually "
                    "derived value assuming 1.5% of investment for "
                    "maintenance plus 27.5 M USD/year for personnel, "
                    "converted to EUR using the ECB USD/EUR reference "
                    "exchange rate for 2022."
                ),
                metadata=ecb_dataset.metadata,
            ),
        )
        return attr

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for refining.

        Manually set to 1 USD/barrel,
        https://link.springer.com/chapter/10.1007/978-3-030-86884-0_3

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        attr = self.opex_specific_variable
        ecb_dataset = ECBDollar2Euro(source_path=self.source_path)
        dollar2euro = ecb_dataset.get_dollar2euro(2022)
        mwh_to_toe = 0.0859845
        ton_to_barrel = 7.46
        opex_variable = ton_to_barrel * dollar2euro * mwh_to_toe
        attr.set_data(
            default_value=opex_variable,
            unit="Euro/MWh",
            source=SourceInformation(
                description=(
                    "The specific variable opex of refining is a manually "
                    "derived value assuming 1 USD/barrel, converted to EUR "
                    "using the ECB USD/EUR reference exchange rate for 2022."
                ),
                metadata=ecb_dataset.metadata,
            ),
        )
        return attr

    # TODO: capacity_existing should be sourced from the Energy Institute
    # Statistical Review of World Energy (refining capacity), which is not
    # yet implemented as a dataset in zen_europe; framework default applies.
