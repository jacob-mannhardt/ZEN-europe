from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, SourceInformation
from zen_europe.datasets.datasets.financial.dea import DEA
from zen_europe.datasets.dataset_collections.district_heating_data import (
    DistrictHeatingData)
from zen_europe.datasets.dataset_collections.heat_demand import HeatDemand

class NaturalGasBoiler(ConversionTechnology):
    """Class containing all data and assumptions for natural gas boilers."""

    name: str = "natural_gas_boiler"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of natural gas boilers to heat.
        """
        return Attribute(
            name="reference_carrier", default_value=["heat"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of natural gas boilers to natural gas.
        """
        return Attribute(
            name="input_carrier", default_value=["natural_gas"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of natural gas boilers to heat.
        """
        return Attribute(
            name="output_carrier", default_value=["heat"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of natural gas boilers.

        """
        attr = self.lifetime
        dea = DEA(source_path=self.source_path)
        data = dea.get_dh_distribution_data()
        lifetime = int(data.loc[("suburban","lifetime","ref"),"value"].iloc[0])
        source = SourceInformation(
            description=(
                "The lifetime of natural gas boilers is based on data from the DEA dataset, "
                "which provides information on the distribution of lifetimes for natural gas boilers. "
                "The specific value used here is the reference value for suburban district heating grids."
            ),
            metadata=dea.metadata,
        )
        attr.set_data(default_value=lifetime, source=source)
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of natural gas boilers.

        """
        attr = self.conversion_factor
        dea = DEA(source_path=self.source_path)
        data = dea.get_dh_distribution_data()
        cf = 1 - data.loc[("suburban","energy_losses","ref"),"value"].iloc[0]/100
        cf = [{"natural_gas": {
            "default_value": 1/cf, "unit": "GW/GW"
            }
            }
        ]
        source = SourceInformation(
            description=(
                "The conversion factor of natural gas boilers is based on data from the DEA dataset, "
                "which provides information on the distribution of energy losses for natural gas boilers. "
                "The specific value used here is the reference value for suburban natural gas boilers."
            ),
            metadata=dea.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr
    
    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of natural gas boilers.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            dea = DEA(source_path=self.source_path)
            data = dea.get_dh_distribution_data()
            construction_time = int(
                data.loc[("suburban","construction_time","ref"),"value"].iloc[0])
            source = SourceInformation(
                description=(
                    "The construction time of natural gas boilers is based on data from the DEA dataset, "
                    "which provides information on the construction time for natural gas boilers. "
                    "The specific value used here is the reference value for suburban natural gas boilers."
                ),
                metadata=dea.metadata,
            )
            attr.set_data(default_value=construction_time, source=source)
            return attr
        else:
            return self.construction_time
        
    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for natural gas boilers.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        dh_dataset = DistrictHeatingData(
            settings=self.settings, source_path=self.source_path)
        capex = dh_dataset.get_capex_specific_conversion(self)
        return capex
    
    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for natural gas boilers.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        dh_dataset = DistrictHeatingData(
            settings=self.settings, source_path=self.source_path)
        opex_fixed = dh_dataset.get_opex_specific_fixed(self)
        return opex_fixed
    
    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for natural gas boilers.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        dh_dataset = DistrictHeatingData(
            settings=self.settings, source_path=self.source_path)
        opex_variable = dh_dataset.get_opex_specific_variable(self)
        return opex_variable
    
    def _set_capacity_limit(self) -> Attribute:
        """
        Sets the capacity limit for natural gas boilers.

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
            dh_dataset = DistrictHeatingData(
                settings=self.settings, source_path=self.source_path)
            attr = dh_dataset.get_capacity_limit(self)
        return attr
    
    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity for natural gas boilers.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        heat_demand_dataset = HeatDemand(
            settings=self.settings, source_path=self.source_path)
        return heat_demand_dataset.get_capacity_existing(self)
        
    
    def _set_max_load(self) -> Attribute:
        """
        Sets the maximum load for natural gas boilers.

        Returns:
            Attribute: An Attribute object containing the maximum load data.
        """
        heat_demand_dataset = HeatDemand(
            settings=self.settings, source_path=self.source_path)

        return heat_demand_dataset.get_max_load(self)
