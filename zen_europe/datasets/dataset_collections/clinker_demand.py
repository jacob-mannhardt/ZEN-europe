from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd


if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset, Element


from zen_creator import Attribute, DatasetCollection
from zen_creator.utils.attribute import SourceInformation

from zen_europe.datasets.datasets.carrier.aidres import Aidres
from zen_europe.datasets.datasets.carrier.british_geological_survey import BritishGeologicalSurvey

class ClinkerDemand(DatasetCollection):
    """Extracting clinker demand data."""

    name = "clinker_demand"

    def __init__(self, source_path: Path | str):
        super().__init__(source_path=source_path)

    def _get_data(self) -> Dict[str, Dataset[Any]]:
        """Load all available data sources."""

        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")

        return {
            "aidres": Aidres(self.source_path),
            "british_geological_survey": BritishGeologicalSurvey(self.source_path),
        }

    def get_clinker_demand(self, element: Element) -> Attribute:
        """
        Get the demand for clinker.

        This function retrieves the clinker demand data for the specified element.
        """
        aidres_dataset = cast(Aidres, self.data["aidres"])
        data = aidres_dataset.get_demand(element)
        bgs_dataset = cast(BritishGeologicalSurvey, self.data["british_geological_survey"])
        
        missing_countries = pd.Index(element.model.config.system.set_nodes).difference(
            data.index)
        
        for country in missing_countries:
            data.loc[country] = bgs_dataset.get_manual_cement_demand(country)
    
        data = data.sort_index() / 8.76 * aidres_dataset.get_CEM2_clinker_ratio()
        
        data.index.name = "node"
        data.name = "demand"

        source = SourceInformation(
            description=(
                "Clinker demand data is derived from the Aidres dataset, which provides "
                "demand data for various industrial sectors. "
                "For countries not covered in the Aidres dataset, "
                " cement demand data from the British Geological Survey is used."
            ),
            metadata=self.metadata,
        )
        return element.demand.set_data(
            source=source,
            df=data,
            unit="t/h",
        )
