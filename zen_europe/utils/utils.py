import pandas as pd

# maps the country names used in the raw source file to NUTS0 node codes,
def convert_country_names(series: pd.Series):
    """ this method converts a series of country names into the node names used here """
    country_names = {
        "Austria": "AT",
        "Belgium": "BE",
        "Bulgaria": "BG",
        "Switzerland": "CH",
        "Czech Republic": "CZ",
        "Czechia": "CZ",
        "Germany": "DE",
        "Denmark": "DK",
        "Estonia": "EE",
        "Greece": "EL",
        "GR": "EL",
        "Spain": "ES",
        "Finland": "FI",
        "France": "FR",
        "Croatia": "HR",
        "Hungary": "HU",
        "Ireland": "IE",
        "Italy": "IT",
        "Lithuania": "LT",
        "Luxembourg": "LU",
        "Latvia": "LV",
        "The Netherlands": "NL",
        "Netherlands": "NL",
        "Norway": "NO",
        "Poland": "PL",
        "Portugal": "PT",
        "Romania": "RO",
        "Sweden": "SE",
        "Slovenia": "SI",
        "Slovakia": "SK",
        "Slovak Republic": "SK",
        "United Kingdom": "UK",
        "UK": "UK",
    }
    series_new = series.apply(
        lambda el: country_names[el] if el in country_names.keys() else None)
    return series_new

def interpolate_missing_years(df: pd.DataFrame) -> pd.DataFrame:
    """Interpolate missing years in a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with years as columns.

    Returns:
        pd.DataFrame: DataFrame with missing years interpolated.
    """
    if isinstance(df, pd.DataFrame):
        assert (
            all(isinstance(col, int) for col in df.columns) 
            and df.columns.dtype == "int64"), (
            "All columns must be numeric (years).")
        # Reindex the columns to include all years from min to max
        df = df.reindex(
            range(df.columns.min(), df.columns.max() + 1), axis=1
        ).interpolate(axis=1)
    elif isinstance(df, pd.Series):
        assert (
            all(isinstance(idx, int) for idx in df.index) 
            and df.index.dtype == "int64"), (
            "All index values must be numeric (years).")
        # Reindex the index to include all years from min to max
        df = df.reindex(
            range(df.index.min(), df.index.max() + 1)
        ).interpolate()
    else:
        raise TypeError("Input must be a pandas DataFrame or Series,"
                        f" but got {type(df).__name__}.")
    return df