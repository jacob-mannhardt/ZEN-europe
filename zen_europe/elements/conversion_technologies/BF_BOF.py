from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class BF_BOF(ConversionTechnology):
    """Class containing all data and assumptions for the blast furnace /
    basic oxygen furnace (BF-BOF) primary steelmaking route."""

    name: str = "BF_BOF"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of BF-BOF to primary steel.
        """
        return Attribute(
            name="reference_carrier", default_value=["primary_steel"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of BF-BOF to hard coal.
        """
        return Attribute(
            name="input_carrier", default_value=["hard_coal"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of BF-BOF to primary steel.
        """
        return Attribute(
            name="output_carrier", default_value=["primary_steel"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of BF-BOF.

        TODO: No lifetime data source has been identified/ported for BF-BOF
        (the legacy pipeline has the same open TODO); framework default
        (NaN) is kept.
        """
        attr = self.lifetime
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of BF-BOF.

        Value based on a hard coal (coke + PCI) consumption of 14.8 GJ per
        ton of primary steel, from Agora Industry (2021), 'Low-carbon
        technologies for the global steel transformation'.
        https://www.agora-industry.org/publications/low-carbon-technologies-for-the-global-steel-transformation
        """
        attr = self.conversion_factor
        cf = [{"hard_coal": {"default_value": 14.8 / 3600, "unit": "GWh/tonproduct"}}]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of BF-BOF is manually derived "
                    "from Agora Industry (2021), 'Low-carbon technologies "
                    "for the global steel transformation'."
                ),
            ),
        )
        return attr

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for BF-BOF.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        attr = self.opex_specific_variable
        attr.set_data(
            default_value=392.1608533,
            unit="Euro/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The variable opex of BF-BOF is manually set based on "
                    "Agora Industry (2021), 'Low-carbon technologies for "
                    "the global steel transformation'."
                ),
            ),
        )
        return attr

    def _set_carbon_intensity_technology(self) -> Attribute:
        """
        Sets the carbon intensity of BF-BOF.

        Process emissions (from the reduction reaction, sintering, coking
        and lime production) net of the emissions already attributed to
        hard coal combustion via its carrier-level carbon intensity, based
        on Agora Industry (2021), 'Low-carbon technologies for the global
        steel transformation'.

        Returns:
            Attribute: An Attribute object containing the carbon intensity data.
        """
        attr = self.carbon_intensity_technology
        # process emissions from reduction (0.28), sintering (0.93), coking
        # (0.4) and lime production (0.18), tCO2/tsteel
        total_emissions = 0.28 + 0.93 + 0.4 + 0.18
        hard_coal_consumption = 14.8 / 3600  # GWh/tonproduct
        # direct combustion carbon intensity of hard coal, tons/MWh
        hard_coal_carbon_intensity = 0.34060
        coal_emissions = hard_coal_consumption * hard_coal_carbon_intensity * 1000
        attr.set_data(
            default_value=total_emissions - coal_emissions,
            unit="ton/tonproduct",
            source=AssumptionInformation(
                description=(
                    "The carbon intensity of BF-BOF is manually derived "
                    "from Agora Industry (2021), 'Low-carbon technologies "
                    "for the global steel transformation', as the sum of "
                    "process emissions (reduction, sintering, coking, lime "
                    "production) net of the combustion emissions already "
                    "attributed to the hard_coal carrier's carbon intensity."
                ),
            ),
        )
        return attr

    # TODO: capex_specific_conversion/opex_specific_fixed should be sourced
    # from the curated "costs_additional_technologies.xlsx" (AddTech)
    # dataset, which is not yet implemented in zen_europe; framework
    # defaults apply.

    # TODO: capacity_existing should be sourced from primary-steel demand
    # (cd.steel_demand times the primary-steel share in the legacy
    # pipeline). A SteelDemand dataset collection exists in zen_europe (see
    # zen_europe/datasets/dataset_collections/steel_demand.py), but its
    # public method is designed to populate a Carrier's `demand` attribute
    # rather than a ConversionTechnology's `capacity_existing`; adapting it
    # is left as a TODO rather than duplicating its internal logic here.
