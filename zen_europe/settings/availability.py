from zen_creator.utils.settings import SettingsCategory


class AvailabilitySettings(SettingsCategory):
    """Carrier availability/import settings."""

    name: str = "availability"

    cap_waste_import: bool = False
    cap_coal_oil_import: bool = False
    annual_cap_coal_oil_import: bool = False
    annual_cap_biomass_import: bool = False
    allow_heat_demand_shedding: bool = False
    allow_all_demand_shedding: bool = False
