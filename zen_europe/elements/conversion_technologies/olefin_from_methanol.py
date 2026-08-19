from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.carrier.aidres import Aidres

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, SourceInformation


class OlefinFromMethanol(ConversionTechnology):
    """Class containing all data and assumptions for olefin production
    from methanol."""

    name: str = "olefin_from_methanol"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of olefin from methanol to olefin.
        """
        return Attribute(
            name="reference_carrier", default_value=["olefin"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of olefin from methanol to methanol and
        electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["methanol", "electricity"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of olefin from methanol to olefin.
        """
        return Attribute(
            name="output_carrier", default_value=["olefin"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of olefin from methanol.

        """
        attr = self.lifetime
        attr.set_data(
            default_value=25,
            source=AssumptionInformation(
                description=(
                    "The lifetime of olefin from methanol is manually set "
                    "to 25 years, assuming a standard industrial technology "
                    "lifetime."
                ),
            ),
        )
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of olefin from methanol.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            attr.set_data(
                default_value=3,
                source=AssumptionInformation(
                    description=(
                        "The construction time of olefin from methanol is "
                        "manually set to 3 years, assuming a standard "
                        "industrial construction timeline."
                    ),
                ),
            )
            return attr
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of olefin from methanol.

        """
        attr = self.conversion_factor
        aidres_dataset = Aidres(source_path=self.source_path)
        cf_dict = aidres_dataset.get_conversion_factors_aidres(self.name)
        cf = [
            {carrier: {"default_value": value, "unit": "GWh/tonproduct"}}
            for carrier, value in cf_dict.items()
        ]
        source = SourceInformation(
            description=(
                "The conversion factor of olefin from methanol is obtained "
                "from the Aidres dataset (Table 32, MeOH-to-olefin route)."
            ),
            metadata=aidres_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    # TODO: capex_specific_conversion/opex_specific_fixed should be sourced
    # from the curated "costs_additional_technologies.xlsx" (AddTech)
    # dataset, which is not yet implemented in zen_europe; framework
    # defaults apply.

    # TODO: capacity_existing has no ported data source for olefin from
    # methanol (legacy pipeline also leaves it at 0); framework default
    # applies.
