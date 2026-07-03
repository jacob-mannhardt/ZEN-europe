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

class IFA(Dataset[pd.DataFrame]):
    """
    International Fertilizer Association dataset class.

    This class implements the specific behavior for the IFA dataset.
    """

    name = "ifa"

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Ammonia demand from Gabrielli et al. (2023) and "
                "the International Fertilizer Association (IFA)"
            ),
            author=["Paolo Gabrielli", 
                    "Lorenzo Rosa",
                    "Matteo Gazzani",
                    "Raoul Meys",
                    "André Bardow",
                    "Marco Mazzotti",
                    "Giovanni Sansavini",
                    "International Fertilizer Association"],
            publication="One Earth",
            publication_year=2023,
            url="https://www.sciencedirect.com/science/article/pii/S2590332223002075",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path / "02-carrier" / "industry" 

    def _set_data(self) -> dict[str, pd.DataFrame]:
        ys = [2020,2050]
        data = {}
        for y in ys:
            df = pd.read_excel(
                self.path / 
                f"Chemical Industry - Summary Calculations Geospatial {y}.xlsx",
                sheet_name="Sheet1")
            data[str(y)] = df
        return data

    # -------- methods ------------------------
    def get_demand(self, element: Carrier) -> Attribute:
        """
        Get the demand of ammonia from the IFA dataset.

        This method retrieves the demand data for ammonia from the IFA dataset
        and returns it as an Attribute object.

        Args:
            element (Carrier): The carrier element for which to get the demand.
        """
        ds = {}
        for y, df in self.data.items():
            d = df[["Country", f"Ammonia production in {y} [1,000 tNH3]"]]
            d["Country"] = convert_country_names(d["Country"])
            d = d.dropna().set_index("Country").squeeze()
            ds[int(y)] = d
        d = pd.concat(ds, axis=1)
        d = interpolate_missing_years(d)
        d = d/8760 * 1000 * element._TON_NH3_TO_GWH
        d = d[(d != 0).all(axis=1)]

        d.index.name = "node"
        d = d.sort_index()

        reference_year = element.config.system.reference_year
        yearly_variation = d.div(d[reference_year], axis=0)
        reference_year_values = d[reference_year]
        reference_year_values.name = "demand"

        source = SourceInformation(
            description=(
                "Ammonia demand from Gabrielli et al. (2023) and the "
                "International Fertilizer Association (IFA). The data was first" \
                " produced by IFA and then processed by Gabrielli et al. (2023)."
                " Converted from 1000 tNH3 to GW (assume constant demand) and "
                "interpolated to fill missing years; the yearly variation is expressed "
                "relative to the reference year."
            ),
            metadata=self.metadata,
        )
        return  element.demand.set_data(
            source=source,
            df=reference_year_values,
            yearly_variations_df=yearly_variation,
            unit="GW",
        )
