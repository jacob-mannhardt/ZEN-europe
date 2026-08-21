from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

import pandas as pd

from zen_europe.datasets.datasets.carrier.material_economics import MaterialEconomics
from zen_europe.utils.constants import Constants
from zen_europe.utils.utils import calculate_capacity_addition_from_cumulative, format_capacity_existing


if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator import Dataset, Element


from zen_creator import Attribute, ConversionTechnology, DatasetCollection
from zen_creator.utils.attribute import SourceInformation

from zen_europe.datasets.datasets.carrier.aidres import Aidres
from zen_europe.datasets.datasets.carrier.british_geological_survey import BritishGeologicalSurvey

class ClinkerData(DatasetCollection):
    """Extracting clinker data data."""

    name = "clinker_data"

    def __init__(self, source_path: Path | str):
        super().__init__(source_path=source_path)

    def _get_data(self) -> Dict[str, Dataset[Any]]:
        """Load all available data sources."""

        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset collection.")

        return {
            "aidres": Aidres(self.source_path),
            "british_geological_survey": BritishGeologicalSurvey(self.source_path),
            "material_economics": MaterialEconomics(self.source_path),
        }

    def _calculate_clinker_demand(self, element: Element) -> Attribute:
        """
        Calculate the clinker demand for the given element.

        This function retrieves the clinker demand data for the specified element.
        It first attempts to get the demand from the Aidres dataset. If the demand
        data is not available in Aidres, it falls back to using data from the
        British Geological Survey (BGS) dataset.

        Args:
            element (Element): The element for which to calculate clinker demand.

        Returns:
            Attribute: An Attribute object containing the clinker demand data.
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
        return data
    
    def get_clinker_demand(self, element: Element) -> Attribute:
        """
        Get the demand for clinker.

        This function retrieves the clinker demand data for the specified element.
        """
        data = self._calculate_clinker_demand(element)

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

    def get_conversion_factor_cement_kiln(
            self, 
            element: ConversionTechnology) -> Attribute:
        """
        Get the conversion factor for cement.

        This function retrieves the cement conversion factor data for the specified element.

        The reference cement fuel is hard coal, which can be substituted by other fuels in the model. 
        """
        attr = element.conversion_factor
        aidres_dataset = cast(Aidres, self.data["aidres"])
        me_dataset = cast(MaterialEconomics, self.data["material_economics"])
        cement_to_clinker = aidres_dataset.get_CEM2_clinker_ratio()
        fuel_consumption_kiln = me_dataset.get_fuel_consumption_cement_kiln()
        cf = [
            {"electricity": {
                "default_value": (
                    0.29 / 
                    (Constants.GJ_PER_MWH * 1000) / 
                    cement_to_clinker), 
                    "unit": "GWh/tonproduct"}},
            {"fuel_for_cement": {
                "default_value": (
                    fuel_consumption_kiln / 
                    (Constants.GJ_PER_MWH * 1000)), 
                "unit": "GWh/tonproduct"}},
        ]
        attr.set_data(
            default_value=cf,
            source=SourceInformation(
                description=(
                    "The conversion factor of cement kilns is "
                    "derived from a fuel consumption of 3.7 GJ per ton of "
                    "clinker  (Material Economics) and an "
                    "electricity consumption of 0.29 GJ per ton of cement (AIDRES), "
                    "rescaled to a clinker basis via the AIDRES "
                    "clinker-to-cement ratio of 0.70."
                    " The reference cement fuel is hard coal, which can be substituted "
                    "by other fuels in the model ('<x>_to_cement_fuel')."
                ),
                metadata=self.metadata,
            ),
        )
        return attr

    def get_capacity_existing_cement_fuel(
            self, element: ConversionTechnology) -> Attribute:
        """
        Get the existing capacity for cement fuel.

        This function retrieves the existing capacity data for cement fuel technologies.
        """
        attr = element.capacity_existing
        aidres_dataset = cast(Aidres, self.data["aidres"])
        me_dataset = cast(MaterialEconomics, self.data["material_economics"])
        share = aidres_dataset.get_share_capacity_existing_cement_fuel()
        assert element.name in share, f"Existing capacity share for {element.name} not found."
        clinker_element = element.model.carriers["clinker"]
        capacity_existing = self._calculate_clinker_demand(clinker_element)
        clinker2fuel = me_dataset.get_fuel_consumption_cement_kiln() / 3600 # GWh/t
        capacity_existing = capacity_existing.rename(
            {"demand": element.settings.time.reference_year - 1},axis=1)
        capacity_existing *= clinker2fuel * share[element.name]
        capacity_existing = calculate_capacity_addition_from_cumulative(
            capacity_existing, element)
        capacity_existing = format_capacity_existing(capacity_existing)
        attr.set_data(
            df=capacity_existing,
            unit="GW",
            source=SourceInformation(
                description=(
                    "The existing capacity for cement fuel technologies is mainly "
                    "derived from the Aidres dataset, which provides "
                    "data on existing capacities for various industrial sectors."
                ),
                metadata=self.metadata,
            ),
        )
        return attr