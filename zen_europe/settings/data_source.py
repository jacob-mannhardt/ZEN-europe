from typing import Literal

from zen_creator.utils.settings import SettingsCategory


class DataSourceSettings(SettingsCategory):
    """Settings controlling which data sources are used."""

    name: str = "data_source"

    use_bnef_capacities: bool = True
    use_full_scigrid_dataset: bool = False
    use_eurostat_heat: bool = True
    use_OG_carbon_storage_limit: bool = True
    use_monthly_entsoe_ntc: bool = True  # TODO remove
    potential_capacity_power_line: Literal["candidates", "tyndp", "both"] = "candidates"
    use_plant_level_hydro_capacity: bool = False 
