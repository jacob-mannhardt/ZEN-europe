from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd

from zen_europe.datasets.datasets.carrier.truck_standard_load_profiles import TruckStandardLoadProfiles

if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset


from zen_creator import Attribute, Carrier, DatasetCollection
from zen_creator.utils.attribute import SourceInformation
from zen_creator.utils.settings import Settings

from zen_europe.datasets.datasets.carrier.eurostat import Eurostat
from zen_europe.datasets.datasets.carrier.standard_load_profiles import (
    StandardLoadProfiles)
from zen_europe.datasets.datasets.carrier.statistical_pocketbook_transport import (
    StatisticalPocketbookTransport
)

import numpy as np

class TruckMileageDemand(DatasetCollection):
    """Extracting truck mileage demand data."""

    name = "truck_mileage_demand"

    def __init__(self, settings: Settings, source_path: Path | str):
        self.settings = settings
        super().__init__(source_path=source_path)

    def _get_data(self) -> Dict[str, Dataset[Any]]:
        """Load all available data sources."""

        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")

        return {
            "eurostat": Eurostat(self.settings, self.source_path),
            "statistical_pocketbook_transport": StatisticalPocketbookTransport(
                self.settings, self.source_path),
            "standard_load_profiles": StandardLoadProfiles(self.source_path),
        }

    def get_demand(self, element: Carrier) -> Attribute:
        """
        Get the truck mileage demand for the specified element.

        """
        # add load profiles
        slp_dataset = TruckStandardLoadProfiles(self.source_path)
        slp = slp_dataset.get_standard_load_profiles()
        # total demand 
        spt_dataset = cast(
            StatisticalPocketbookTransport, 
            self.data["statistical_pocketbook_transport"])
        total_demand = spt_dataset.get_total_mileage(element)

        slp_country = pd.DataFrame(data=np.outer(slp, total_demand), index=slp.index,
                                 columns=total_demand.index)
        
        slp_country = slp_dataset.shift_by_timezone(slp_country)

        source = SourceInformation(
            description=(
                "Total truck mileage demand is derived from the Statistical Pocketbook "
                "Transport dataset, which provides data on passenger and truck mileage "
                "in the EU. The standard load profiles for trucks is obtained from"
                "Borlaug et al. (2021). The final truck mileage demand is calculated by "
                "multiplying the total truck mileage by the weighted standard load "
                "profiles."
            ),
            metadata=self.metadata,
        )
        return element.demand.set_data(
            source=source,
            df=slp,
            unit="megatkm/hour",
        )
