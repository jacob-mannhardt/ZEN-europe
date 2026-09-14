from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.ccs_conversion_factor import CCSConversionFactor
from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.technology.IOGP_carbon_storage_projects import IOGPCarbonStorageProjects
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import AssumptionInformation, AssumptionInformation, Attribute, RetrofittingTechnology


class BiomassPlantCCS(RetrofittingTechnology):
    """Class containing all data and assumptions for biomass power plants
    retrofitted with post-combustion carbon capture (CCS)."""

    name: str = "biomass_plant_CCS"
    base_technology_name: str = "biomass_plant"

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of biomass plant CCS to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of biomass plant CCS to electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["electricity"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of biomass plant CCS to carbon.
        """
        return Attribute(
            name="output_carrier", default_value=["carbon"],
            element=self
        )

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of biomass plant CCS to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of biomass plant CCS.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of biomass plant CCS.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for biomass plant CCS.

        Following the legacy pipeline, this is the delta between the
        CCS-equipped plant's cost-database entry and the base `biomass_plant`
        technology's entry, divided by `retrofit_flow_coupling_factor` so that
        it is expressed per unit of captured CO2 rather than per unit of power
        capacity.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements[self.base_technology_name]
        return tech_db.get_capex_specific_conversion_retrofit(
            self, base_technology=base_tech)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for biomass
        plant CCS.

        Like the capex, this is the delta between the CCS-equipped plant's
        cost-database entry and that of the base `biomass_plant`, divided by
        `retrofit_flow_coupling_factor`.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements[self.base_technology_name]
        return tech_db.get_opex_specific_fixed_retrofit(
            self, base_technology=base_tech)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        biomass plant CCS.

        Like the capex, this is the delta between the CCS-equipped plant's
        cost-database entry and that of the base `biomass_plant`, divided by
        `retrofit_flow_coupling_factor`.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements[self.base_technology_name]
        return tech_db.get_opex_specific_variable_retrofit(
            self, base_technology=base_tech)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of biomass plant CCS.

        """
        ccs_cf_db = CCSConversionFactor(
            settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements[self.base_technology_name]
        cf = ccs_cf_db.get_conversion_factor_CCS(
            element=self, base_tech=base_tech)
        return cf

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of biomass plant CCS.

        """
        ccs_cf_db = CCSConversionFactor(
            settings=self.settings, source_path=self.source_path)
        base_tech = self.model.elements[self.base_technology_name]
        return ccs_cf_db.get_retrofit_flow_coupling_factor(
            element=self, base_tech=base_tech)

    
    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of biomass plant CCS.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        if self.settings.investment.use_existing_capacities:
            igop_projects = IOGPCarbonStorageProjects(source_path=self.source_path)
            return igop_projects.get_capacity_existing_capture(self)
        else:
            attr = self.capacity_existing
            attr.set_data(
                default_value=0,
                df=None,
                source=AssumptionInformation(
                    description=(
                        "We do not consider existing capacities."
                    ),
                ),
            )
            return attr

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of biomass plant CCS.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
