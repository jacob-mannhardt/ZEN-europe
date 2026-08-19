from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.financial.dea import DEA

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, RetrofittingTechnology, SourceInformation


class CementPostComb(RetrofittingTechnology):
    """Class containing all data and assumptions for cement kilns
    retrofitted with post-combustion carbon capture (CCS)."""

    name: str = "cement_post_comb"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of cement post-combustion capture to
        carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of cement post-combustion capture to fuel
        for cement and electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["fuel_for_cement", "electricity"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of cement post-combustion capture to carbon
        and district heat.
        """
        return Attribute(
            name="output_carrier", default_value=["carbon", "district_heat"],
            element=self
        )

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of cement post-combustion
        capture to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of cement post-combustion capture.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of cement post-combustion capture.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of cement post-combustion capture.

        Values from the DEA technology catalogue for carbon capture,
        transport and storage (Post-combustion carbon capture in a cement
        plant), assuming the fuel-for-cement input is directly converted
        into heat for the capture process.
        https://ens.dk/en/our-services/projections-and-models/technology-data/technology-data-carbon-capture-transport-and
        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_cement_post_comb()
        source = SourceInformation(
            description=(
                "The conversion factor of cement post-combustion capture "
                "is a manually derived value based on the DEA technology "
                "catalogue for carbon capture, transport and storage "
                "(Post-combustion carbon capture in a cement plant), "
                "assuming the fuel-for-cement input is directly converted "
                "into heat for the capture process."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for cement
        post-combustion capture.

        `take_delta_cost_from_base_tech` is `False` for this technology
        (the base `cement_kiln` technology has no cost-database coverage of
        its own), so the cost-database value is used directly (absolute
        cost), matching the legacy pipeline.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for cement
        post-combustion capture.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        cement post-combustion capture.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of cement post-combustion
        capture.

        TODO: In the legacy pipeline this is computed as
        `clinker_carbon_intensity (0.54 tCO2/tClinker, Material Economics
        (2019), 'Industrial Transformation 2050') *
        carbon_capture_rate_cement (0.9,
        https://ens.dk/en/our-services/projections-and-models/technology-data/technology-data-carbon-capture-transport-and)`,
        unit-scaled from a clinker basis to the `cement_kiln` base
        technology's capacity units. Left at the framework default (1.0)
        pending that unit-scaling implementation.
        """
        attr = self.retrofit_flow_coupling_factor
        return attr

    # TODO: capacity_existing should be sourced from the IOGP CCS database
    # (technologies present in the cluster map), which is not yet
    # implemented as a dataset in zen_europe; framework default applies.
