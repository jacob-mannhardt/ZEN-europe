from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from zen_creator.elements import Element
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData
from zen_creator.utils.attribute import Attribute, SourceInformation
from zen_europe.utils.utils import convert_country_names, interpolate_missing_years

import pandas as pd

class SciGridIGGIELGNC1(Dataset[pd.DataFrame]):
    """
    SciGrid IGGIELGNC-1 dataset class for natural gas.

    This class implements the specific behavior for the SciGrid IGGIELGNC-1 dataset.

    Significant data inaccuracies are observed for storage data
    points that are only found in the INET dataset, especially for the UK. 
    Thus, we exclude those storages
    with only an INET source ID.
    """

    name = "scigrid_iggielgnc1"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "SciGRID_gas IGGIELGNC-1"
            ),
            author=["Jan Diettrich", 
                    "Adam Pluta", 
                    "Wided Medjroubi", 
                    "Jan Dasenbrock", 
                    "Javier Sandoval"],
            publication="DLR - German Aerospace Center",
            publication_year=2021,
            url="https://zenodo.org/records/5509988",
            note="Significant data inaccuracies are observed for storage data "
                "points that are only found in the INET dataset, especially for the UK. "
                "Thus, we exclude those storages with only an INET source ID.",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path / "03-technology" / "natural_gas" 

    def _set_data(self) -> dict[str, pd.DataFrame]:
        border_points_raw = pd.read_csv(
            self.path / "IGGIELGNC1_BorderPoints.csv", delimiter=";")
        storages_raw = pd.read_csv(
            self.path / "IGGIELGNC1_Storages.csv", delimiter=";")
        select_storage_data = pd.Series(index=storages_raw.index, data=False)
        for storage in storages_raw.index:
            split_source_id = storages_raw.loc[storage, "source_id"].split(",")
            if len(split_source_id) > 1 or "INET" not in split_source_id[0]:
                select_storage_data[storage] = True
        storages_raw = storages_raw[select_storage_data]
        border_points = border_points_raw["param"].apply(
            lambda item: pd.Series(ast.literal_eval(str(item))))
        border_points = border_points.replace({"GR": "EL", "GB": "UK"})
        storages = storages_raw["param"].apply(
            lambda item: pd.Series(ast.literal_eval(str(item))))
        storages["nuts_id_0"] = storages_raw["country_code"].replace(
            {"GR": "EL", "GB": "UK"})
        return {
            "border_points": border_points,
            "storages": storages
        }

    def get_pipeline_availability(self,element: Element) -> tuple[pd.DataFrame, pd.Series]:
        """
        Get the pipeline availability data.

        This function retrieves the pipeline availability data from the SciGrid IGGIELGNC-1 dataset.
        """
        border_points = self.data["border_points"]
        import_gas = pd.DataFrame(
            index=element.model.config.system.set_nodes, 
            columns=["import", "export"], 
            data=0,dtype=float)
        import_gas_RU = pd.Series(
            index=element.model.config.system.set_nodes, data=0,dtype=float)
        nodes_RU = ["RU", "UA", "BY", "MD"]
        nodes_turkstream = {"from": "TR", "to": "BG"}
        for node in element.model.config.system.set_nodes:
            import_gas_node = border_points[(border_points["to_country"] == node) & (
                ~border_points["from_country"].isin(
                    element.model.config.system.set_nodes))]
            export_gas_node = border_points[(border_points["from_country"] == node) & (
                ~border_points["to_country"].isin(element.model.config.system.set_nodes)
                )]
            import_gas_node = import_gas_node[import_gas_node["from_country"] != "XX"]
            export_gas_node = export_gas_node[export_gas_node["to_country"] != "XX"]
            if not import_gas_node.empty:
                import_gas.loc[node, "import"] += (
                    import_gas_node["max_cap_from_to_M_m3_per_d"] * 
                    import_gas_node["GCV_mean_kWh_per_m3"]).squeeze().sum()
                import_gas.loc[node, "export"] += (
                    import_gas_node["max_cap_to_from_M_m3_per_d"] 
                    * import_gas_node["GCV_mean_kWh_per_m3"]).squeeze().sum()
                # import from "Russian" countries
                if import_gas_node["from_country"].isin(nodes_RU).any():
                    import_gas_node_RU = import_gas_node[
                        import_gas_node["from_country"].isin(nodes_RU)]
                    import_gas_RU.loc[node] += (
                        import_gas_node_RU["max_cap_from_to_M_m3_per_d"] 
                        * import_gas_node_RU["GCV_mean_kWh_per_m3"]
                        ).squeeze().sum()
                # TurkStream
                elif (
                    import_gas_node["from_country"] == nodes_turkstream["from"]
                    ).any() and (
                        import_gas_node["to_country"] == nodes_turkstream["to"]).any():
                    import_gas_node_RU = import_gas_node[
                        (import_gas_node["from_country"] == nodes_turkstream["from"]
                         ) & (import_gas_node["to_country"] == nodes_turkstream["to"])]
                    import_gas_RU.loc[node] += (
                        import_gas_node_RU["max_cap_from_to_M_m3_per_d"] * 
                        import_gas_node_RU["GCV_mean_kWh_per_m3"]).squeeze().sum()
            elif not export_gas_node.empty:
                import_gas.loc[node, "export"] += (
                    export_gas_node["max_cap_from_to_M_m3_per_d"] * 
                    export_gas_node["GCV_mean_kWh_per_m3"]).squeeze().sum()
                import_gas.loc[node, "import"] += (
                    export_gas_node["max_cap_to_from_M_m3_per_d"] * 
                    export_gas_node["GCV_mean_kWh_per_m3"]).squeeze().sum()
                # export to "Russian" countries
                if export_gas_node["to_country"].isin(nodes_RU).any():
                    export_gas_node_RU = export_gas_node[
                        export_gas_node["to_country"].isin(nodes_RU)]
                    import_gas_RU.loc[node] += (
                        export_gas_node_RU["max_cap_to_from_M_m3_per_d"] * 
                        export_gas_node_RU["GCV_mean_kWh_per_m3"]).squeeze().sum()
                # TurkStream
                elif (
                    export_gas_node["to_country"] == nodes_turkstream["from"]
                    ).any() and (
                        export_gas_node["from_country"] == nodes_turkstream["to"]).any():
                    export_gas_node_RU = export_gas_node[
                        (export_gas_node["to_country"] == nodes_turkstream["from"]) & (
                            export_gas_node["from_country"] == nodes_turkstream["to"])]
                    import_gas_RU.loc[node] += (
                        export_gas_node_RU["max_cap_to_from_M_m3_per_d"] * 
                        export_gas_node_RU["GCV_mean_kWh_per_m3"]).squeeze().sum()
        import_gas = import_gas[(import_gas != 0).any(axis=1)].sort_index()
        import_gas_RU = import_gas_RU[import_gas_RU != 0].sort_index()
        import_gas /= 24
        import_gas.index.name = "node"
        import_gas_RU /= 24
        import_gas_RU.index.name = "node"
        return import_gas, import_gas_RU

class SciGridGIE(Dataset[pd.DataFrame]):
    """
    SciGrid GIE dataset class for LNG.

    This class implements the specific behavior for the SciGrid GIE dataset.

    We only use GIE for LNG terminals, as the other SciGrid datasets show inaccuracies
    for LNG terminals.
    """

    name = "scigrid_gie"
    _GCV_LNG = 11.65 # most common value in the scigrid database, in kWh/m3
    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "SciGRID_gas GIE"
            ),
            author=["Jan Diettrich", 
                    "Adam Pluta", 
                    "Wided Medjroubi", 
                    "Jan Dasenbrock", 
                    "Javier Sandoval"],
            publication="DLR - German Aerospace Center",
            publication_year=2021,
            url="https://zenodo.org/records/4750985",
            note="We only use GIE for LNG terminals, "
                "as the other SciGrid datasets show inaccuracies for LNG terminals.",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path / "03-technology" / "lng" 

    def _set_data(self) -> pd.DataFrame:
        lng_terminals_raw = pd.read_csv(
            self.path / "GIE_LNGs.csv", delimiter=";")
        lng_terminals = lng_terminals_raw["param"].apply(lambda item: pd.Series(ast.literal_eval(str(item))))
        lng_terminals["nuts_id_0"] = lng_terminals_raw["country_code"].replace({"GR": "EL", "GB": "UK"})
        lng_terminals["name"] = lng_terminals_raw["name"]
        return lng_terminals
    
    def _calculate_existing_capacity_lng(self,element: Element) -> pd.DataFrame:
        """
        Calculate the existing capacity of LNG terminals.

        This method calculates the existing capacity of LNG terminals based on the
        provided data and returns it as a DataFrame.

        Returns:
            A DataFrame containing the existing capacity of LNG terminals.
        """
        lng_terminals = self.data.copy()
        lng_terminals["capa_GWh_per_d"] = (self._GCV_LNG * 
            lng_terminals["median_cap_store2pipe_M_m3_per_d"])
        lng_terminals["start_year"] = 2010 # assume all terminals are available from 2010 onwards, as we do not have data on the construction year
        lng_terminals_scigrid = lng_terminals.groupby(
            ["nuts_id_0", "start_year"]).sum(numeric_only=True)["capa_GWh_per_d"]
        capacity_existing = pd.DataFrame(index=lng_terminals_scigrid.index)
        capacity_existing["capacity_existing"] = lng_terminals_scigrid / 24
        common_countries = capacity_existing.index.get_level_values(0).intersection(
            element.model.config.system.set_nodes)
        capacity_existing = capacity_existing.loc[common_countries]
        capacity_existing.index.names = ["node", "year_construction"]

        capacity_existing = capacity_existing.sort_index()
        return capacity_existing