from __future__ import annotations

import ast
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from zen_creator.elements import Element
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

import pandas as pd

class ETNSOE(Dataset[pd.DataFrame]):
    """
    ENTSOE dataset class for natural gas availability.

    This class implements the specific behavior for the ENTSOE dataset.
    """

    name = "entsoe"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "ENTSOE Transparency Platform"
            ),
            author=["ENTSOE"],
            publication="ENTSOE",
            publication_year=datetime.now().year,
            url=f"https://transparency.entsoe.eu/",
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> pd.Series:
        return pd.Series()  

