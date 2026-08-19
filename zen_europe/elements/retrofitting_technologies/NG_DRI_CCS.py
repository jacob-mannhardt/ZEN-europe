from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.financial.dea import DEA

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, RetrofittingTechnology, SourceInformation


class NG_DRI_CCS(RetrofittingTechnology):
    """Class containing all data and assumptions for the natural-gas-based
    direct reduced iron (NG-DRI) route retrofitted with post-combustion
    carbon capture (CCS)."""

    name: str = "NG_DRI_CCS"

    # tCO2eq/tsteel, Agora Industry (2021), 'Low-carbon technologies for the
    # global steel transformation',
    # https://www.agora-industry.org/publications/low-carbon-technologies-for-the-global-steel-transformation
    CARBON_CAPTURE_NG_DRI = 0.35

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of NG-DRI CCS to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of NG-DRI CCS to electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["electricity"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of NG-DRI CCS to carbon.
        """
        return Attribute(
            name="output_carrier", default_value=["carbon"], element=self
        )

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of NG-DRI CCS to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of NG-DRI CCS.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of NG-DRI CCS.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of NG-DRI CCS.

        Value based on an electricity demand of 0.23 GJ per ton of steel
        (Agora Industry (2021), 'Low-carbon technologies for the global
        steel transformation'), rescaled from a per-steel to a
        per-captured-carbon basis via the NG-DRI carbon capture rate.
        """
        attr = self.conversion_factor
        cf = [{"electricity": {
            "default_value": 0.23 / 3.6 / self.CARBON_CAPTURE_NG_DRI,
            "unit": "GWh/kilotons"}}]
        dea_dataset = DEA(source_path=self.source_path)
        source = SourceInformation(
            description=(
                "The conversion factor of NG-DRI CCS is manually derived "
                "from an electricity demand of 0.23 GJ per ton of steel "
                "(Agora Industry (2021), 'Low-carbon technologies for the "
                "global steel transformation'), rescaled to a per-captured-"
                "carbon basis via the NG-DRI carbon capture rate of "
                f"{self.CARBON_CAPTURE_NG_DRI} tCO2eq/tsteel."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for NG-DRI CCS.

        `take_delta_cost_from_base_tech` is `False` for this technology
        (the base `NG_DRI` technology has no cost-database coverage of its
        own), so the cost-database value is used directly (absolute cost),
        matching the legacy pipeline.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for NG-DRI
        CCS.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        NG-DRI CCS.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of NG-DRI CCS.

        TODO: In the legacy pipeline this is set to the NG-DRI carbon
        capture rate (`CARBON_CAPTURE_NG_DRI` = 0.35 tCO2eq/tsteel, Agora
        Industry (2021), 'Low-carbon technologies for the global steel
        transformation'), then unit-scaled against the `NG_DRI` base
        technology's capacity units. That unit-scaling step has not been
        ported; left at the framework default (1.0) pending that
        implementation.
        """
        attr = self.retrofit_flow_coupling_factor
        return attr

    # TODO: capacity_existing has no ported data source for NG-DRI CCS (the
    # technology is absent from the legacy pipeline's IOGP capture/cluster
    # maps); framework default applies.
