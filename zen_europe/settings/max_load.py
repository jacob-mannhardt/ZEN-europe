from zen_creator.utils.settings import SettingsCategory


class MaxLoadSettings(SettingsCategory):
    """Max-load settings."""

    name: str = "max_load"

    use_seasonal_nuclear_max_load: bool = True # NOTE DONE
    use_nodal_nuclear_max_load: bool = True # NOTE DONE
