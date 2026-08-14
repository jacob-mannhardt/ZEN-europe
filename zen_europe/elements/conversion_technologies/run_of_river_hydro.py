from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.hydro_existing_capacity import HydroExistingCapacity
from zen_europe.datasets.dataset_collections.potential_capacity_renewables import PotentialCapacityRenewables
from zen_europe.datasets.dataset_collections.run_of_river_hydro_max_load import RunOfRiverHydroMaxLoad
from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.technology.pan_european_climate_database import PanEuropeanClimateDatabase

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, ConversionTechnology, SourceInformation


class RunOfRiverHydro(ConversionTechnology):
    """Class containing all data and assumptions for run-of-river hydro."""

    name: str = "run-of-river_hydro"

    ENTSOE_PSR_ROR = "B11"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of run-of-river hydro to electricity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of run-of-river hydro to an empty list.

        This is because run-of-river hydro do not have an input carrier,
        as they convert solar energy directly into electricity.
        """
        return Attribute(name="input_carrier", default_value=[], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of run-of-river hydro to electricity.
        """
        return Attribute(
            name="output_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of run-of-river hydro.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of run-of-river hydro.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                        settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time
        
    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of run-of-river hydro.

        """
        attr = self.conversion_factor
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for run-of-river hydro.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)
    
    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for run-of-river hydro.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)
    
    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for run-of-river hydro.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    def _set_capacity_limit(self) -> Attribute:
        """
        Sets the capacity limit for run-of-river hydro.

        Returns:
            Attribute: An Attribute object containing the capacity limit data.
        """
        data = self.capacity_existing.df
        capacity_limit = data.groupby(level=0).sum()
        capacity_limit.name = "capacity_limit"
        attr = self.capacity_limit.set_data(
            df=capacity_limit,
            source=SourceInformation(
                description=(
                    "The capacity limit is set to the sum of the"
                    "historical capacity additions across all years."
                ),
                metadata=self.metadata,
            ),
            unit="GW",
        )
        return attr

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity for run-of-river hydro.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        hydro_capacity = HydroExistingCapacity(
            settings=self.settings,
            source_path=self.source_path,
            set_nodes=self.model.config.system.set_nodes
        )
        attr = hydro_capacity.get_capacity_existing(self)
        return attr

    def _set_max_load(self) -> Attribute:
        """
        Sets the maximum load for run-of-river hydro.

        Returns:
            Attribute: An Attribute object containing the maximum load data.
        """
        ror_max_load = RunOfRiverHydroMaxLoad(
            settings=self.settings,
            source_path=self.source_path,
            set_nodes=self.model.config.system.set_nodes
        )
        return ror_max_load.get_max_load(self)