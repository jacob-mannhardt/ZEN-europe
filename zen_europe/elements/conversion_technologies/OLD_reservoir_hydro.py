from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.hydro_existing_capacity import HydroExistingCapacity
from zen_europe.datasets.dataset_collections.lifetime_expectation import LifetimeExpectation
from zen_europe.datasets.dataset_collections.run_of_river_hydro_max_load import RunOfRiverHydroMaxLoad
from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.technology.pan_european_climate_database import PanEuropeanClimateDatabase

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, SourceInformation


class ReservoirHydro(ConversionTechnology):
    """Class containing all data and assumptions for reservoir hydro power plants."""

    name: str = "reservoir_hydro"

    ENTSOE_PSR = "B12"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of reservoir hydro to electricity.
        """
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of reservoir hydro to an empty list.

        This is because reservoir hydro does not have an input carrier,
        as it converts the potential energy of stored water directly into
        electricity.
        """
        return Attribute(name="input_carrier", default_value=[], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of reservoir hydro to electricity.
        """
        return Attribute(
            name="output_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of reservoir hydro.

        Per default, we assume a lifetime of 200 years to keep 
        the existing capacities in the model. Otherwise, we use the real
        lifetime of the technology. 

        """
        if self.settings.investment.use_200y_lifetime_hydro:
            attr = self.lifetime
            return attr.set_data(
                default_value=200,
                source=AssumptionInformation(
                    description=(
                        "The lifetime of reservoir hydro is set to 200 years, "
                        "as specified in the investment settings."
                    ),
                )
            )
        else:
            lifetime_expectation = LifetimeExpectation(source_path=self.source_path)
            return lifetime_expectation.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of reservoir hydro.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                        settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of reservoir hydro.

        """
        attr = self.conversion_factor
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for reservoir hydro.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for reservoir hydro.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for reservoir hydro.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    def _set_capacity_limit(self) -> Attribute:
        """
        Sets the capacity limit for reservoir hydro.

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
            data = self.capacity_existing.df
            capacity_limit = data.groupby(level=0).sum()
            capacity_limit.name = "capacity_limit"
            attr.set_data(
                df=capacity_limit,
                source=SourceInformation(
                    description=(
                        "The capacity limit is set to the sum of the "
                        "historical capacity additions across all years."
                    ),
                    metadata=self.capacity_existing.sources[-1].metadata,
                ),
                unit="GW",
            )
        return attr

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity for reservoir hydro.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        if self.settings.investment.use_existing_capacities:
            hydro_capacity = HydroExistingCapacity(
                settings=self.settings,
                source_path=self.source_path,
                set_nodes=self.model.config.system.set_nodes
            )
            if self.settings.data_source.use_plant_level_hydro_capacity:
                attr = hydro_capacity.get_capacity_existing_plant_level_data(self)
            else:
                attr = hydro_capacity.get_capacity_existing_entsoe_data(self)
            return attr
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

    def _set_max_load(self) -> Attribute:
        """
        Sets the maximum load for reservoir hydro.

        Returns:
            Attribute: An Attribute object containing the maximum load data.
        """
        ror_max_load = RunOfRiverHydroMaxLoad(
            settings=self.settings, 
            source_path=self.source_path,
            set_nodes=self.model.config.system.set_nodes)
        return ror_max_load.get_max_load(self)
