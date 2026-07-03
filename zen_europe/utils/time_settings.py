from zen_creator.model import Model

# TODO move somewhere else, maybe to zen_creator.utils.time_settings
def get_optimization_years(model:Model) -> list[int]:
    """Get the optimization years based on the last year.

    Returns:
        A list of integers representing the optimization years.
    """
    last_year: int = 2050
    return list(range(2020, last_year + 1, 5))