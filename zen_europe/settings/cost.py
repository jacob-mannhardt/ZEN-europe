from zen_creator.utils.settings import SettingsCategory


class CostSettings(SettingsCategory):
    """Cost-related settings."""

    name: str = "cost"

    use_learning_curves: bool = True
    use_nodal_biomass_prices: bool = False
    use_expensive_DAC: bool = False
    assume_oil_price_for_diesel_and_gasoline: bool = False
