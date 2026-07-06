from typing import Literal

from zen_creator.utils.settings import SettingsCategory


class MaxLoadSettings(SettingsCategory):
    """Max-load and fuel-substitution settings."""

    name: str = "max_load"

    use_fuel_substitution: bool = False  # TODO remove
    use_district_heating_fuel_substitution: Literal["full", "mixed", "none"] = "mixed"  # TODO remove
    use_seasonal_nuclear_max_load: bool = True
    use_nodal_nuclear_max_load: bool = True
