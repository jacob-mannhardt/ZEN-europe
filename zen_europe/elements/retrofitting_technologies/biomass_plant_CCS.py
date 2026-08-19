from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, RetrofittingTechnology


class BiomassPlantCCS(RetrofittingTechnology):
    """Class containing all data and assumptions for biomass power plants
    retrofitted with post-combustion carbon capture (CCS)."""

    name: str = "biomass_plant_CCS"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of biomass plant CCS to electricity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of biomass plant CCS to biomass.
        """
        return Attribute(
            name="input_carrier", default_value=["biomass"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of biomass plant CCS to electricity and
        carbon.
        """
        return Attribute(
            name="output_carrier", default_value=["electricity", "carbon"],
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

        Note: the legacy pipeline computes this as a delta between the
        CCS-equipped plant's cost-database entry and the base
        `biomass_plant` technology's entry (gated by a
        `take_delta_cost_from_base_tech` flag, `True` for this technology),
        divided by `retrofit_flow_coupling_factor`. Since that coupling
        factor is not implemented here (see `_set_retrofit_flow_coupling_factor`),
        this method instead returns the absolute cost-database value for
        `biomass_plant_CCS` (e.g. EUREF's "Steam turbine biomass solid
        conventional w. CCS" entry) as a simplification; TODO revisit once
        the coupling factor is implemented.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for biomass
        plant CCS.

        Note: see the `take_delta_cost_from_base_tech` caveat documented in
        `_set_capex_specific_conversion`.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        biomass plant CCS.

        Note: see the `take_delta_cost_from_base_tech` caveat documented in
        `_set_capex_specific_conversion`.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of biomass plant CCS.

        TODO: In the legacy pipeline this is derived from a cost-database
        efficiency comparison between `biomass_plant` and
        `biomass_plant_CCS`; left empty pending that comparison.
        """
        attr = self.conversion_factor
        return attr

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of biomass plant CCS.

        TODO: In the legacy pipeline this is computed as
        `carbon_intensity_carrier_fuel["biomass"] * (1 / efficiency_base)
        * CCS_capture_rate`, with `CCS_capture_rate = 0.88` (Yang et al.
        2021, https://www.sciencedirect.com/science/article/pii/S136403212100318X,
        Table 2, VPSA) and the biomass carbon intensity and base-plant
        efficiency both requiring cross-referencing a Carrier element and
        the technology cost database's efficiency data. Left at the
        framework default (1.0) pending that implementation.
        """
        attr = self.retrofit_flow_coupling_factor
        return attr

    # TODO: capacity_existing has no ported data source for biomass plant
    # CCS (the technology is absent from the legacy pipeline's IOGP
    # capture/cluster maps); framework default applies.
