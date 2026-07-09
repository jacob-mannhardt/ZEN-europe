from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from zen_creator.elements.carriers.carrier import Carrier
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData
from zen_creator.utils.attribute import Attribute

import pandas as pd

_KTOE2GWH = 1 / 0.0859845  # ktoe (useful energy) -> GWh

class BFE(Dataset[pd.DataFrame]):
    """
    Bundesamt für Energie (BFE) dataset class.

    This class implements the specific behavior for the BFE dataset.
    """

    name = "bfe"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Energieverbrauch nach Verwendungszweck"
            ),
            author=["Bundesamt für Energie (BFE)"],
            publication="BFE",
            publication_year=2025,
            url="https://www.bfe.admin.ch/bfe/de/home/versorgung/statistik-und-geodaten/energiestatistiken/energieverbrauch-nach-verwendungszweck.html",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path / "02-carrier" / "heat" / "12361-VWZ_Webtabellen_2024.xlsx"

    def _set_data(self) -> dict[str, pd.DataFrame]:
        data_res = pd.read_excel(
            self.path, sheet_name="Tabelle17",
            skiprows=5,usecols="B:AA")
        data_ser = pd.read_excel(
            self.path, sheet_name="Tabelle26",
            skiprows=5,usecols="B:AA")
        data_res = data_res.set_index("Verwendungszweck") / 3.6 * 1000 # from PJ to GWh
        data_ser = data_ser.set_index("Verwendungszweck") / 3.6 * 1000 # from PJ to GWh
        return {"residential": data_res.sort_index(), "service": data_ser.sort_index()}

    # -------- methods ------------------------
    def get_demand(self, element: Carrier) -> Attribute:
        """
        Get the CH heat demand 

        Args:
            element (Carrier): The carrier element for which to get the demand.
        """
        year_time_series = element.model.settings.time.year_time_series
        data_res = self.data["residential"].loc[
            ["Raumwärme", "Warmwasser"], year_time_series]
        data_ser = self.data["service"].loc[
            ["Raumwärme", "Warmwasser"], year_time_series]
        data_res = data_res.rename({
            "Raumwärme": "space_heating", "Warmwasser": "water_heating"
        })
        data_ser = data_ser.rename({
            "Raumwärme": "space_heating", "Warmwasser": "water_heating"
        })
        data = pd.concat({"residential": data_res, "tertiary": data_ser})
        return data
