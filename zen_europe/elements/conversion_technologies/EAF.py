from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class EAF(ConversionTechnology):
    """Class containing all data and assumptions for the electric arc
    furnace (EAF) secondary steelmaking route."""

    name: str = "EAF"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of EAF to secondary steel.
        """
        return Attribute(
            name="reference_carrier", default_value=["secondary_steel"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of EAF to electricity and hard coal.
        """
        return Attribute(
            name="input_carrier", default_value=["electricity", "hard_coal"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of EAF to secondary steel.
        """
        return Attribute(
            name="output_carrier", default_value=["secondary_steel"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of EAF.

        TODO: No lifetime data source has been identified/ported for EAF
        (the legacy pipeline has the same open TODO); framework default
        (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of EAF.

        Values based on Agora Industry (2021), 'Low-carbon technologies for
        the global steel transformation': 2.46 GJ electricity and 0.37 GJ
        hard coal (electrode/additives) per ton of secondary steel.
        https://www.agora-industry.org/publications/low-carbon-technologies-for-the-global-steel-transformation
        """
        attr = self.conversion_factor
        cf = [
            {"electricity": {"default_value": 2.46 / 3600, "unit": "GWh/tonproduct"}},
            {"hard_coal": {"default_value": 0.37 / 3600, "unit": "GWh/tonproduct"}},
        ]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of EAF is manually derived from "
                    "Agora Industry (2021), 'Low-carbon technologies for "
                    "the global steel transformation'."
                ),
            ),
        )
        return attr

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for EAF.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        attr = self.opex_specific_variable
        attr.set_data(
            default_value=548.244,
            unit="Euro/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The variable opex of EAF is manually set based on "
                    "Agora Industry (2021), 'Low-carbon technologies for "
                    "the global steel transformation'."
                ),
            ),
        )
        return attr

    def _set_carbon_intensity_technology(self) -> Attribute:
        """
        Sets the carbon intensity of EAF.

        Returns:
            Attribute: An Attribute object containing the carbon intensity data.
        """
        attr = self.carbon_intensity_technology
        attr.set_data(
            default_value=0.01,
            unit="ton/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The carbon intensity of EAF is manually set based on "
                    "Agora Industry (2021), 'Low-carbon technologies for "
                    "the global steel transformation', representing "
                    "residual process emissions not attributable to the "
                    "electricity/hard_coal carriers' carbon intensity."
                ),
            ),
        )
        return attr

    # TODO: capex_specific_conversion/opex_specific_fixed should be sourced
    # from the curated "costs_additional_technologies.xlsx" (AddTech)
    # dataset, which is not yet implemented in zen_europe; framework
    # defaults apply.

    # TODO: capacity_existing should be sourced from secondary-steel demand
    # (cd.steel_demand times the secondary-steel share in the legacy
    # pipeline). A SteelDemand dataset collection exists in zen_europe (see
    # zen_europe/datasets/dataset_collections/steel_demand.py), but its
    # public method is designed to populate a Carrier's `demand` attribute
    # rather than a ConversionTechnology's `capacity_existing`; adapting it
    # is left as a TODO rather than duplicating its internal logic here.
