# Import concrete settings categories to register them (side effect) with
# zen_creator's SettingsCategory registry, so they become queryable as
# model.settings.<name> (e.g. model.settings.time).
from .availability import AvailabilitySettings  # noqa: F401
from .cost import CostSettings  # noqa: F401
from .data_source import DataSourceSettings  # noqa: F401
from .emissions import EmissionsSettings  # noqa: F401
from .investment import InvestmentSettings  # noqa: F401
from .max_load import MaxLoadSettings  # noqa: F401
from .time import TimeSettings  # noqa: F401

__all__ = [
    "TimeSettings",
    "InvestmentSettings",
    "CostSettings",
    "EmissionsSettings",
    "DataSourceSettings",
    "AvailabilitySettings",
    "MaxLoadSettings",
]
