from typing import Literal

from zen_creator.utils.settings import SettingsCategory


class CostSettings(SettingsCategory):
    """Cost-related settings."""

    name: str = "cost"

    use_cost_comparison: bool = True
    use_learning_curves: bool = True
    min_max_mean_costs: Literal["mean", "min", "max"] = "mean"
    use_seasonal_fuel_prices: bool = False
    use_nodal_gas_prices: bool = False
    use_nodal_biomass_prices: bool = False
    take_mean_carrier_prices: bool = True
    use_expensive_DAC: bool = False
    use_cheaper_demand_shedding: bool = False
    assume_oil_price_for_diesel_and_gasoline: bool = False
