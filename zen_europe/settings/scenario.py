from zen_creator.utils.settings import SettingsCategory


class ScenarioSettings(SettingsCategory):
    """Scenario settings."""

    name: str = "scenario"

    run_default_scenario: bool = True
    sensitivity_demand: bool = True
    sensitivity_discount_rate: bool = False
    sensitivity_biomass: bool = False
    sensitivity_no_diffusion_rate: bool = True