from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, RetrofittingTechnology


class NaturalGasTurbineCCS(RetrofittingTechnology):
    """Class containing all data and assumptions for natural gas turbines
    retrofitted with post-combustion carbon capture (CCS)."""

    name: str = "natural_gas_turbine_CCS"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of natural gas turbine CCS to electricity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of natural gas turbine CCS to natural gas.
        """
        return Attribute(
            name="input_carrier", default_value=["natural_gas"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of natural gas turbine CCS to electricity and
        carbon.
        """
        return Attribute(
            name="output_carrier", default_value=["electricity", "carbon"],
            element=self
        )

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of natural gas turbine CCS to
        carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of natural gas turbine CCS.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of natural gas turbine CCS.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for natural gas
        turbine CCS.

        Following the legacy pipeline, this is the delta between the
        CCS-equipped plant's cost-database entry and the base
        `natural_gas_turbine` technology's entry, divided by
        `retrofit_flow_coupling_factor` so that it is expressed per unit of
        captured CO2 rather than per unit of power capacity.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements["natural_gas_turbine"]
        return tech_db.get_capex_specific_conversion_retrofit(
            self, base_technology=base_tech)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for natural
        gas turbine CCS.

        Like the capex, this is the delta between the CCS-equipped plant's
        cost-database entry and that of the base `natural_gas_turbine`,
        divided by `retrofit_flow_coupling_factor`.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements["natural_gas_turbine"]
        return tech_db.get_opex_specific_fixed_retrofit(
            self, base_technology=base_tech)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        natural gas turbine CCS.

        Like the capex, this is the delta between the CCS-equipped plant's
        cost-database entry and that of the base `natural_gas_turbine`,
        divided by `retrofit_flow_coupling_factor`.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements["natural_gas_turbine"]
        return tech_db.get_opex_specific_variable_retrofit(
            self, base_technology=base_tech)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of natural gas turbine CCS.

        TODO: In the legacy pipeline this is derived from a cost-database
        efficiency comparison between `natural_gas_turbine` and
        `natural_gas_turbine_CCS`; left empty pending that comparison.
        """
        attr = self.conversion_factor
        return attr

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of natural gas turbine CCS.

        TODO: In the legacy pipeline this is computed as
        `carbon_intensity_carrier_fuel["natural_gas"] * (1 / efficiency_base)
        * CCS_capture_rate`, with `CCS_capture_rate = 0.88` (Yang et al.
        2021, https://www.sciencedirect.com/science/article/pii/S136403212100318X,
        Table 2, VPSA) and the natural gas carbon intensity and base-plant
        efficiency both requiring cross-referencing a Carrier element and
        the technology cost database's efficiency data. Left at the
        framework default (1.0) pending that implementation.
        """
        attr = self.retrofit_flow_coupling_factor
        return attr

    # TODO: capacity_existing should be sourced from the IOGP CCS database
    # (technologies present in the capture/cluster maps), which is not yet
    # implemented as a dataset in zen_europe; framework default applies.
