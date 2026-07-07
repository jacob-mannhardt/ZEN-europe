from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd


if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset, Element


from zen_creator import Attribute, DatasetCollection
from zen_creator.utils.attribute import SourceInformation
from zen_creator.utils.settings import Settings

from zen_europe.datasets.datasets.carrier.aidres import Aidres
from zen_europe.datasets.datasets.carrier.eurostat import Eurostat

class OlefinDemand(DatasetCollection):
    """Extracting olefin demand data."""

    name = "olefin_demand"

    def __init__(self, settings: Settings, source_path: Path | str):
        self.settings = settings
        super().__init__(source_path=source_path)

    def _get_data(self) -> Dict[str, Dataset[Any]]:
        """Load all available data sources."""

        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")

        return {
            "aidres": Aidres(self.source_path),
            "eurostat": Eurostat(source_path=self.source_path,settings=self.settings),
        }

    def get_olefin_demand(self, element: Element) -> Attribute:
        """
        Get the demand for olefin.

        The idea is to use the naphtha demand from Eurostat as a proxy for olefin demand, 
        since naphtha is a key feedstock for olefin production. 
        The function retrieves the naphtha demand data
         and processes it to obtain the olefin demand.
        """
        aidres_dataset = cast(Aidres, self.data["aidres"])
        eurostat_dataset = cast(Eurostat, self.data["eurostat"])
        eurostat_data = eurostat_dataset.get_naphtha_demand()
        common_countries = eurostat_data.index.intersection(
            element.model.config.system.set_nodes)
        missing_countries = pd.Index(element.model.config.system.set_nodes).difference(
            eurostat_data.index)
        d = eurostat_data.loc[common_countries, eurostat_dataset.eurostat_year]
        for country in missing_countries:
            if country == "CH":
                d.loc[country] = 0 # no olefin demand in Switzerland
            else:
                raise ValueError(f"Missing olefin demand data for country {country}.")
        d = d/8760 # convert from GWh/a to GWh/h

        naphtha2olefin = aidres_dataset.get_conversion_factors_aidres(
            "olefin_from_naphtha")["naphtha"]
        
        d = d / naphtha2olefin # [GWh/h/[GWh/t]] = [t/h]
        
        d.index.name = "node"
        d.name = "demand"

        source = SourceInformation(
            description=(
                "Olefin demand derived from naphtha demand from Eurostat, "
                "with conversion factors from the Aidres dataset." \
                "The naphtha demand is used as a proxy for olefin demand, "
                "since naphtha is a key feedstock for olefin production."
            ),
            metadata=self.metadata,
        )
        return element.demand.set_data(
            source=source,
            df=d,
            unit="t/h",
        )
    
    