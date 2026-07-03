from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator.elements.carriers.carrier import Carrier
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData
from zen_creator.utils.attribute import Attribute, SourceInformation
from zen_europe.utils.utils import convert_country_names, interpolate_missing_years

import pandas as pd

class MaterialEconomics(Dataset[pd.DataFrame]):
    """
    Material economics dataset class.

    This class implements the specific behavior for the Material Economics dataset.
    """

    name = "material_economics"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Industrial Transformation 2050 - "
                "Pathways to Net-Zero Emissions from EU Heavy Industry"
            ),
            author=["Material Economics"],
            publication="Material Economics",
            publication_year=2019,
            url="https://materialeconomics.com/publications/publication/industrial-transformation-2050",
        )

    def _set_path(self) -> Path | None:
        return None

    def _set_data(self) -> dict[str, pd.DataFrame]:
        # TODO there is no data to be implemented
        data = {}
        return data

    # -------- methods ------------------------    
    def get_secondary_steel_ratios(self) -> tuple[float]:
        """
        Get the secondary steel ratios.

        This method retrieves the secondary steel ratios at the beginning and the end
        and returns them as a tuple of floats.

        The share at the beginning is measured from the screen.
        The share at the end is chosen between 50% (CCS pathway) and 70% (circular economy)

        Returns:
            A tuple of floats representing the secondary steel ratios.
        """
        secondary_steel_share_beginning = 1-2.7/3.5
        secondary_steel_share_end = 0.6
        return (secondary_steel_share_beginning, secondary_steel_share_end)
        