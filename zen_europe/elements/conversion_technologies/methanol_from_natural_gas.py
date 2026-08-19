from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class MethanolFromNaturalGas(ConversionTechnology):
    """Class containing all data and assumptions for methanol production
    from natural gas."""

    name: str = "methanol_from_natural_gas"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of methanol from natural gas to methanol.
        """
        return Attribute(
            name="reference_carrier", default_value=["methanol"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of methanol from natural gas to natural gas
        and electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["natural_gas", "electricity"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of methanol from natural gas to methanol.
        """
        return Attribute(
            name="output_carrier", default_value=["methanol"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of methanol from natural gas.

        """
        attr = self.lifetime
        attr.set_data(
            default_value=25,
            source=AssumptionInformation(
                description=(
                    "The lifetime of methanol from natural gas is manually "
                    "set to 25 years, based on the cost study reported in "
                    "https://www.sciencedirect.com/science/article/pii/S1876610217313280 "
                    "(p. 10)."
                ),
            ),
        )
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of methanol from natural gas.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            attr.set_data(
                default_value=3,
                source=AssumptionInformation(
                    description=(
                        "The construction time of methanol from natural gas "
                        "is manually set to 3 years, assuming a standard "
                        "industrial construction timeline."
                    ),
                ),
            )
            return attr
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of methanol from natural gas.

        Values from the cost study reported in
        https://www.sciencedirect.com/science/article/pii/S1876610217313280
        (p. 10).
        """
        attr = self.conversion_factor
        cf = [
            {"natural_gas": {"default_value": 1760 / 1163, "unit": "GWh/GWh"}},
            {"electricity": {"default_value": 18.47 / 1163, "unit": "GWh/GWh"}},
        ]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of methanol from natural gas is "
                    "manually derived from the cost study reported in "
                    "https://www.sciencedirect.com/science/article/pii/S1876610217313280 "
                    "(p. 10)."
                ),
            ),
        )
        return attr

    # TODO: capex_specific_conversion/opex_specific_fixed should be sourced
    # from the curated "costs_additional_technologies.xlsx" (AddTech)
    # dataset, which is not yet implemented in zen_europe; framework
    # defaults apply.

    # TODO: capacity_existing should be sourced from methanol demand
    # (cd.methanol_demand in the legacy pipeline). A MethanolDemand dataset
    # collection exists in zen_europe (see
    # zen_europe/datasets/dataset_collections/methanol_demand.py), but its
    # public method is designed to populate a Carrier's `demand` attribute
    # rather than a ConversionTechnology's `capacity_existing`; adapting it
    # is left as a TODO rather than duplicating its internal logic here.
