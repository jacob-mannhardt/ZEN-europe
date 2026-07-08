from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd




if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset


from zen_creator import Attribute, Carrier, DatasetCollection
from zen_creator.utils.attribute import SourceInformation
from zen_creator.utils.settings import Settings

from zen_europe.datasets.datasets.carrier.jrc_idees import JRCIDEES
from zen_europe.datasets.datasets.carrier.eurostat import Eurostat
from zen_europe.datasets.datasets.carrier.when2heat import When2Heat
from zen_europe.datasets.datasets.carrier.desnz import DESNZ

class HeatDemand(DatasetCollection):
    """Extracting heat demand data."""

    name = "heat_demand"

    def __init__(self, settings: Settings, source_path: Path | str):
        self.settings = settings
        super().__init__(source_path=source_path)

    def _get_data(self) -> Dict[str, Dataset[Any]]:
        """Load all available data sources."""

        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")

        return {
            "jrc_idees": JRCIDEES(self.source_path),
            "when2heat": When2Heat(self.settings, self.source_path),
            "eurostat": Eurostat(self.settings, self.source_path),
            "desnz": DESNZ(self.source_path),
        }

    def get_demand(self, element: Carrier) -> Attribute:
        """
        Get the heat demand for the specified element.

        """
        jrc_idees_dataset = cast(JRCIDEES, self.data["jrc_idees"])
        eurostat_dataset = cast(Eurostat, self.data["eurostat"])
        desnz_dataset = cast(DESNZ, self.data["desnz"])
        data_jrc = jrc_idees_dataset.get_demand(element)
        missing_countries = pd.Index(element.model.config.system.set_nodes).difference(
            data_jrc.index.get_level_values("node").unique()
        )
        for country in missing_countries:
            # TODO THIS WILL CHANGE
            if country == "CH":
                data_jrc.loc[country] = data_jrc.loc["AT"]
            elif country == "NO" or country == "UK":
                # residential heat demand from Eurostat
                data_res = eurostat_dataset.get_heat()
                data_res = data_res.loc[country]
                # services for UK from ECUK
                if country == "UK":
                    data_ser = desnz_dataset.get_service_demand(element)
                    data_ser = data_ser.loc[country]
                    data_res = pd.concat({"residential": data_res, "services": data_ser})

            else:
                raise ValueError(
                    f"Missing heat demand data for country {country}."
                )
        # add heating profiles
        when2heat_dataset = cast(When2Heat, self.data["when2heat"])
        profiles = when2heat_dataset.get_profiles(element)

        # align jrc_idees's (node, sector, category) labels with when2heat's
        # (node, house_type, category) column naming convention
        sector_to_house_type = {"residential": "RES", "tertiary": "COM"}
        jrc_to_profile_category = {"space_heating": "space", "water_heating": "water"}
        data_jrc = data_jrc.rename(index=sector_to_house_type, level="sector")
        data_jrc = data_jrc.rename(index=jrc_to_profile_category, level="category")
        data_jrc.index = data_jrc.index.set_names(["node", "house_type", "category"])

        # scale each (node, house_type, category) profile by its annual demand,
        # then sum residential/tertiary and space/water heating per country
        demand = (profiles * data_jrc).T.groupby(level="node").sum().T
        demand = demand / 1e6 # convert to GW
        

        source = SourceInformation(
            description=(
                "The gasoline and diesel price data is assumed to follow the oil price"
                " from the BNEF dataset, "
                "and the crack spread is assumed to be stationary."
            ),
            metadata=self.metadata,
        )
        return element.price_import.set_data(
            source=source,
            default_value=default_value,
            yearly_variations_df=yearly_variations_df,
            unit="Euro/MWh",
        )
    
    