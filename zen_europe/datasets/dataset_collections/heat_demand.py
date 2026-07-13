from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd




if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset


from zen_creator import Attribute, Carrier, DatasetCollection, Element
from zen_creator.utils.attribute import SourceInformation
from zen_creator.utils.settings import Settings

from zen_europe.datasets.datasets.carrier.jrc_idees import JRCIDEES
from zen_europe.datasets.datasets.carrier.eurostat import Eurostat
from zen_europe.datasets.datasets.carrier.when2heat import When2Heat
from zen_europe.datasets.datasets.carrier.desnz import DESNZ
from zen_europe.datasets.datasets.carrier.bfe import BFE
from zen_europe.datasets.datasets.carrier.energifaktanorge import Energifaktanorge


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
            "bfe": BFE(self.source_path),
            "energifaktanorge": Energifaktanorge(self.source_path),
        }

    def get_demand(self, element: Carrier) -> Attribute:
        """
        Get the heat demand for the specified element.

        """
        demand = self._calculate_demand(element)

        source = SourceInformation(
            description=(
                "The heat demand data is derived from multiple sources:"
                "First,"
                " the JRC IDEES dataset provides useful thermal energy services "
                "for most countries. "
                "Second, the Eurostat dataset offers residential heat demand data "
                "for NO and UK. "
                "Third, the DESNZ dataset contains tertiary heat demand for the UK. "
                "Fourth, the BFE dataset provides heat demand data for CH. "
                "Finally, the Energifaktanorge dataset provides tertiary heat demand "
                "for NO. "
            ),
            metadata=self.metadata,
        )
        return element.price_import.set_data(
            source=source,
            df=demand,
            unit="GW",
        )
    
    def _calculate_demand(self, element: Element) -> pd.Series:
        """
        Calculate the heat demand for the specified element.

        """
        
        jrc_idees_dataset = cast(JRCIDEES, self.data["jrc_idees"])
        eurostat_dataset = cast(Eurostat, self.data["eurostat"])
        desnz_dataset = cast(DESNZ, self.data["desnz"])
        bfe_dataset = cast(BFE, self.data["bfe"])
        energifaktanorge_dataset = cast(Energifaktanorge, self.data["energifaktanorge"])
        data_jrc = jrc_idees_dataset.get_demand(element).squeeze()
        missing_countries = pd.Index(element.model.config.system.set_nodes).difference(
            data_jrc.index.get_level_values("node").unique()
        )
        for country in missing_countries:
            if country == "CH":
                data = bfe_dataset.get_demand(element)
            elif country == "NO" or country == "UK":
                # residential heat demand from Eurostat
                data_res = eurostat_dataset.get_total_heat_household().squeeze()
                data_res = data_res.loc[country]
                # tertiary heat demand for UK from ECUK
                if country == "UK":
                    data_ser = desnz_dataset.get_service_demand(element)
                else:
                    data_ser = energifaktanorge_dataset.get_service_demand(element)
                data = pd.concat({"residential": data_res, "tertiary": data_ser})
                data = data.squeeze()
            else:
                raise ValueError(
                    f"Missing heat demand data for country {country}."
                )
            data.index.names = ["sector","category"]
            data = pd.concat({country: data}, names=["node"])
            data_jrc = pd.concat([data_jrc, data])
        # add heating profiles
        when2heat_dataset = cast(When2Heat, self.data["when2heat"])
        profiles = when2heat_dataset.get_profiles()

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

        demand.index.name = "time"
        return demand
    
    
    def _calculate_heating_share_household(self) -> pd.DataFrame:
        """
        Calculate the heating share of all household heating technologies.

        Returns:
            pd.DataFrame: A DataFrame containing the heating shares
            for all household heating technologies.
        """
        eurostat_dataset = cast(Eurostat, self.data["eurostat"])
        household_heat = eurostat_dataset.get_heat_household_technology()
        # average COP
        when2heat_dataset = cast(When2Heat, self.data["when2heat"])
        cop_data = when2heat_dataset.get_COP()
        cop_data = cop_data.xs("floor",level="category", axis=1).mean()
        common_nodes = cop_data.index.intersection(
            household_heat.index.get_level_values(1).unique()
        )
        cop_data = cop_data.loc[common_nodes]
        electricity_hp = household_heat.loc["heat_pump"].div(cop_data-1,axis=0)
        electricity_hp = electricity_hp.fillna(0)
        electricity_eb = household_heat.loc["electricity"] - electricity_hp
        electricity_eb = pd.concat([electricity_eb],keys=["electrode_boiler"])
        household_heat = pd.concat([household_heat, electricity_eb]).sort_index()
        household_heat = household_heat.drop("electricity")
        household_heat = household_heat.rename(index={"heat": "district_heating_grid"})
        share_household_heat = household_heat.div(
            household_heat.groupby(level=1).sum(), axis=1)
        share_household_heat.columns = share_household_heat.columns.astype(int)
        
        # swiss data is missing in Eurostat, so we use BFE data for CH
        bfe_dataset = cast(BFE, self.data["bfe"])
        share_CH = bfe_dataset.get_share_household()
        common_years = share_CH.columns.intersection(share_household_heat.columns)
        share_CH = share_CH.loc[:, common_years]
        share_CH = pd.concat([share_CH],keys=["CH"], names=["node"])
        share_CH = share_CH.swaplevel(0, 1).sort_index()
        share_household_heat = pd.concat([share_household_heat, share_CH])
        share_household_heat = share_household_heat.sort_index().sort_index(axis=1)
        share_household_heat = share_household_heat.bfill(axis=1)

        return share_household_heat 
    
    def _calculate_heating_share_DH(self) -> pd.DataFrame:
        """
        Calculate the heating share of electricity demand for district heating.
        """
        eurostat_dataset = cast(Eurostat, self.data["eurostat"])
        district_heat = eurostat_dataset.get_heat_dh_technology()
        # average COP
        when2heat_dataset = cast(When2Heat, self.data["when2heat"])
        cop_data = when2heat_dataset.get_COP()
        cop_data = cop_data.xs("floor",level="category", axis=1).mean()
        electricity_hp_dh = district_heat.loc["heat_pump_DH"].div(cop_data-1,axis=0)
        electricity_hp_dh = electricity_hp_dh.fillna(0)
        electricity_eb_dh = district_heat.loc["electricity_DH"] - electricity_hp_dh
        electricity_eb_dh = pd.concat([electricity_eb_dh],keys=["electrode_boiler_DH"])
        electricity_eb_dh = electricity_eb_dh.clip(lower=0)
        district_heat = pd.concat([district_heat, electricity_eb_dh]).sort_index()
        district_heat = district_heat.drop("electricity_DH")
        share_district_heat = district_heat.div(
            district_heat.groupby(level=1).sum(), axis=1)
        raise NotImplementedError("This method is not yet implemented for CH values.")        
        return share_district_heat