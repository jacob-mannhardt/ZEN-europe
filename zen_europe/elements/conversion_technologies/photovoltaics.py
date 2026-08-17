from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.lifetime_expectation import LifetimeExpectation
from zen_europe.datasets.dataset_collections.potential_capacity_renewables import PotentialCapacityRenewables
from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.technology.irena_solar_capacity import IRENASolarCapacity
from zen_europe.datasets.datasets.technology.pan_european_climate_database import PanEuropeanClimateDatabase

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology


class Photovoltaics(ConversionTechnology):
    """Class containing all data and assumptions for photovoltaics."""

    name: str = "photovoltaics"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of photovoltaics to electricity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of photovoltaics to an empty list.

        This is because photovoltaics do not have an input carrier,
        as they convert solar energy directly into electricity.
        """
        return Attribute(name="input_carrier", default_value=[], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of photovoltaics to electricity.
        """
        return Attribute(
            name="output_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of photovoltaics.

        """
        lifetime_expectation = LifetimeExpectation(source_path=self.source_path)
        return lifetime_expectation.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of district heating grids.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                        settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time
        
    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of photovoltaics.

        """
        attr = self.conversion_factor
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for photovoltaics.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)
    
    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for photovoltaics.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)
    
    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for photovoltaics.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    def _set_capacity_limit(self) -> Attribute:
        """
        Sets the capacity limit for photovoltaics.

        Returns:
            Attribute: An Attribute object containing the capacity limit data.
        """
        attr = self.capacity_limit
        if not self.settings.investment.allow_investment:
            attr.set_data(
                default_value=0,
                source=AssumptionInformation(
                    description=(
                        "The capacity limit is set to 0, "
                        "as investment is not allowed."
                    ),
                ),
            )
        else:
            pcr = PotentialCapacityRenewables(
                source_path=self.source_path)
            attr = pcr.get_capacity_limit(self)
        return attr

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity for photovoltaics.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        irena = IRENASolarCapacity(source_path=self.source_path)
        return irena.get_capacity_existing(self)

    def _set_max_load(self) -> Attribute:
        """
        Sets the maximum load for photovoltaics.

        Returns:
            Attribute: An Attribute object containing the maximum load data.
        """
        pecd = PanEuropeanClimateDatabase(
            settings=self.settings, 
            source_path=self.source_path)
        return pecd.get_max_load(self)