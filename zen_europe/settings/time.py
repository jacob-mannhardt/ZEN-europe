from zen_creator.utils.settings import SettingsCategory


class TimeSettings(SettingsCategory):
    """Time-horizon settings."""

    name: str = "time"

    reference_year: int = 2022
    last_year: int = 2050
    year_time_series: int = 2019
    interval_between_years: int = 2

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