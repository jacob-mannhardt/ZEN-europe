from zen_creator.utils.settings import SettingsCategory


class EmissionsSettings(SettingsCategory):
    """Emissions and carbon-budget settings."""

    name: str = "emissions"

    use_carbon_budget: bool = True
    use_carbon_annual_limit: bool = True
    use_intermediate_emission_goal: bool = True
    use_annual_limit_overshoot: bool = True
    use_EU_ETS_cap: bool = False
    use_detailed_carbon_intensity: bool = True  # TODO remove
    use_only_CO2: bool = True
    use_only_public_electricity_and_heat: bool = True
    use_precovid_aviation_shipping_emissions: bool = False
    allow_hard_coal_export_emission_credit: bool = False
    temperature_increase: float = 1.5
    probability_carbon_budget: float = 0.5
    calculate_budget_from_ETS: bool = False
    use_EU_ETS_cap_ETS1only: bool = False
    use_adjusted_ETS_to_keep_carbon_budget: bool = True
