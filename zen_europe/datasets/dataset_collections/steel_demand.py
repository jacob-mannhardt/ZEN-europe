from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd


if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset, Element


from zen_creator import Attribute, DatasetCollection
from zen_creator.utils.attribute import SourceInformation

from zen_europe.datasets.datasets.carrier.aidres import Aidres
from zen_europe.datasets.datasets.carrier.manual_steel_demand import (Eurofer,
                                                                      WorldSteel,
                                                                      TradeEconomics)
from zen_europe.datasets.datasets.carrier.material_economics import MaterialEconomics

class SteelDemand(DatasetCollection):
    """Extracting steel demand data."""

    name = "steel_demand"

    def __init__(self, source_path: Path | str):
        super().__init__(source_path=source_path)

    def _get_data(self) -> Dict[str, Dataset[Any]]:
        """Load all available data sources."""

        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")

        return {
            "aidres": Aidres(self.source_path),
            "eurofer": Eurofer(self.source_path),
            "worldsteel": WorldSteel(self.source_path),
            "trade_economics": TradeEconomics(self.source_path),
            "material_economics": MaterialEconomics(self.source_path),
        }

    def get_steel_demand(self, element: Element) -> Attribute:
        """
        Get the demand for steel.

        This function retrieves the steel demand data for the specified element.
        """
        aidres_dataset = cast(Aidres, self.data["aidres"])
        data = aidres_dataset.get_demand(element)
        eurofer_dataset = cast(Eurofer, self.data["eurofer"])
        worldsteel_dataset = cast(WorldSteel, self.data["worldsteel"])
        trade_economics_dataset = cast(TradeEconomics, self.data["trade_economics"])
        material_economics_dataset = cast(
            MaterialEconomics, self.data["material_economics"])
        missing_countries = pd.Index(element.model.config.system.set_nodes).difference(
            data.index)
        
        for country in missing_countries:
            if country == "CH":
                data.loc[country] = (
                    eurofer_dataset.get_manual_steel_demand_eurofer(country))
            elif country == "UK":
                data.loc[country] = (
                    worldsteel_dataset.get_manual_steel_demand_worldsteel(country))
            elif country == "NO":
                data.loc[country] = (
                    trade_economics_dataset.get_manual_steel_demand_trade_economics(
                        country))
            else:
                raise ValueError(
                    f"Steel demand data for country {country} is not available in the "
                    "Aidres dataset or any of the manual datasets (Eurofer, WorldSteel, "
                    "TradeEconomics). Please provide the necessary data for this country."
                )
        
        d = data.sort_index() / 8.76

        secondary_steel_share_beginning, secondary_steel_share_end = (
            material_economics_dataset.get_secondary_steel_ratios())
        if element.name == "secondary_steel":
            rat_start = secondary_steel_share_beginning
            rat_end = secondary_steel_share_end/rat_start
        else:
            rat_start = 1-secondary_steel_share_beginning
            rat_end = (1-secondary_steel_share_end)/rat_start

        d = d * rat_start
        d.index.name = "node"
        d.name = "demand"
        
        years = element.model.settings.time.get_optimization_years()

        d_yearly_variation = pd.Series(index=years, dtype=float)
        d_yearly_variation.iloc[0] = 1
        d_yearly_variation.iloc[-1] = rat_end
        d_yearly_variation = d_yearly_variation.interpolate(method="index")
        d_yearly_variation.index.name = "year"
        d_yearly_variation.name = "demand_yearly_variation"

        source = SourceInformation(
            description=(
                "Steel demand data is derived from multiple sources. The main source"
                "is the Aidres dataset. "
                "Additional manual data for missing countries is obtained from the "
                "following datasets:"
                "Eurofer, WorldSteel, and TradeEconomics. "
                "The secondary steel ratios are derived from the Material Economics dataset."
            ),
            metadata=self.metadata,
        )
        return element.demand.set_data(
            source=source,
            df=d,
            yearly_variations_df=d_yearly_variation,
            unit="t/h",
        )
    
    