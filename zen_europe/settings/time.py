from typing import Optional

from scipy.odr import Model
from zen_creator.utils.settings import SettingsCategory


class TimeSettings(SettingsCategory):
    """Time-horizon settings."""

    name: str = "time"

    unaggregated_time_steps_per_year: int = 8760
    conduct_time_series_aggregation: bool = True
    aggregated_time_steps_per_year: int = 100
    reference_year: int = 2022
    last_year: int = 2050
    year_time_series: int = 2019
    total_hours_per_year: Optional[int] = None
    optimized_years: Optional[int] = None
    interval_between_years: int = 2
    use_rolling_horizon: bool = False
    years_in_rolling_horizon: int = 2
    years_in_decision_horizon: int = 1

    @property
    def _optimization_years(self) -> list[int]:
        """Get the optimization years based on the last year.

        Returns:
            A list of integers representing the optimization years.
        """
        return list(range(
            self.reference_year, self.last_year + 1
            ))
    
    def get_optimization_years(self) -> list[int]:
        """Get the optimization years based on the last year.

        Returns:
            A list of integers representing the optimization years.
        """
        return self._optimization_years