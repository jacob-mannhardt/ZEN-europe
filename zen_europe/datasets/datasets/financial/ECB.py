from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from datetime import datetime

import pandas as pd
import scipy.stats as stats
from zen_creator import Dataset
from zen_creator.datasets.datasets.metadata import MetaData


class ECBInflation(Dataset[pd.DataFrame]):
    """Dataset class for ECB data."""

    name = "ecb_inflation"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="HICP - Overall index, Euro area, Monthly",
            author=["European Central Bank"],
            publication="European Central Bank",
            publication_year=datetime.now().year,
            url="https://data.ecb.europa.eu/",
        )

    def _set_path(self) -> Path | None:
        return None  # ECB data is accessed directly via URL, no local path needed

    # ----- Property overwrites -----

    # ----- Load and format Data -----

    def _set_data(self) -> pd.DataFrame:
        """Method to get the inflation rate from ECB data."""
        url = "https://data-api.ecb.europa.eu/service/data/ICP/M.U2.N.000000.4.ANR?format=csvdata"
        df = pd.read_csv(url, usecols=["TIME_PERIOD", "OBS_VALUE"])

        period_parts = df["TIME_PERIOD"].astype(str).str.split("-", n=1, expand=True)
        df["year"] = pd.to_numeric(period_parts[0], errors="raise").astype(int)
        df["month"] = pd.to_numeric(period_parts[1], errors="raise").astype(int)
        df["obs_value"] = pd.to_numeric(df["OBS_VALUE"], errors="raise").astype(float)

        if df.isna().values.any():
            raise ValueError(
                "Data contains NaN values after conversion. "
                "Please check the source data."
            )

        df["inflation_factor"] = 1.0 + df["obs_value"] / 100.0

        inflation_data = df.groupby("year", sort=True)["inflation_factor"].agg(
            lambda values: float(stats.gmean(values.to_numpy(dtype=float)))
        )
        return inflation_data.to_frame(name="inflation_rate")

    # ------ Outward facing functions ------

    def get_inflation_rate(self, base_year: int, target_year: int) -> float:
        """Method to calculate the inflation rate between two years."""
        if base_year >= target_year:
            by = target_year
            ty = base_year
            exp = -1
        else:
            by = base_year
            ty = target_year
            exp = 1
        inflation_rates = pd.to_numeric(
            self.data.loc[by : ty - 1, "inflation_rate"],
            errors="raise",
        )
        return float((inflation_rates.to_numpy(dtype=float).prod())**exp)


class ECBDollar2Euro(Dataset[pd.DataFrame]):
    """Dataset class for ECB data."""

    name = "ecb_dollar_to_euro"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="US dollar/Euro ECB reference exchange rate, Monthly",
            author=["European Central Bank"],
            publication="European Central Bank",
            publication_year=datetime.now().year,
            url="https://data.ecb.europa.eu/data/datasets/EXR/EXR.M.USD.EUR.SP00.A",
        )

    def _set_path(self) -> Path | None:
        return None  # ECB data is accessed directly via URL, no local path needed
    
    # ----- Property overwrites -----

    # ----- Load and format Data -----

    def _set_data(self) -> pd.DataFrame:
        """Method to get the dollar-to-euro conversion rate from ECB data."""
        url = "https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A?format=csvdata"
        df = pd.read_csv(url, usecols=["TIME_PERIOD", "OBS_VALUE"])

        period_parts = df["TIME_PERIOD"].astype(str).str.split("-", n=1, expand=True)
        df["year"] = pd.to_numeric(period_parts[0], errors="raise").astype(int)
        df["month"] = pd.to_numeric(period_parts[1], errors="raise").astype(int)
        df["obs_value"] = pd.to_numeric(df["OBS_VALUE"], errors="raise").astype(float)

        if df.isna().values.any():
            raise ValueError(
                "Data contains NaN values after conversion. "
                "Please check the source data."
            )


        euro2dollar = df.groupby("year")["obs_value"].mean()
        return euro2dollar.to_frame(name="euro2dollar")

    # ------ Outward facing functions ------

    def get_dollar2euro(self, year: int) -> float:
        """Method to calculate the dollar-to-euro conversion rate for a given year."""
        euro2dollar = pd.to_numeric(
            self.data.loc[year, "euro2dollar"],
            errors="raise",
        )
        return 1/euro2dollar