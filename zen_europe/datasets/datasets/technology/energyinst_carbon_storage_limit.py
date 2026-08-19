from __future__ import annotations

from pathlib import Path

from zen_creator import Attribute, SourceInformation
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

import pandas as pd

from zen_europe.utils.utils import convert_country_names, format_capacity_existing

class OGExtractionCarbonStorageLimit(Dataset[pd.DataFrame]):
    """
    Dataset class to calculate the capacity limit for carbon storage based on the 
    extraction of oil and gas. The idea is that the injection capacity of CO2 storage
    is limited by the amount of oil and gas that has been extracted, as the storage
    sites are often located in depleted oil and gas fields. The dataset uses the
    Energy Institute's data on oil and gas extraction to estimate the potential CO2
    storage capacity in Europe. 

    """

    name = "OG_carbon_storage_limit"
    # density https://static-content.springer.com/esm/art%3A10.1038%2Fs41558-021-01175-7/MediaObjects/41558_2021_1175_MOESM1_ESM.pdf p. 17
    DENSITY_OIL = 800 # kg/m3
    DENSITY_NATURAL_GAS = 150 # kg/m3
    DENSITY_CO2 = 700 # kg/m3
    # conversion factor from Bkg to EJ https://ocw.tudelft.nl/wp-content/uploads/Summary_table_with_heating_values_and_CO2_emissions.pdf
    BKGNG2EJ = 0.0381 # EJ/Bkg
    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Energy Institute Statistical Review of World Energy"
            ),
            author=["Energy Institute"],
            publication="Energy Institute",
            publication_year=2023,
            url="https://www.energyinst.org/statistical-review",
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return (
            Path(self.source_path) / 
            "03-technology" / 
            "potential_capacity_carbon_storage" / 
            "Statistical Review of World Energy Data.xlsx")

    def _set_data(self) -> pd.DataFrame:
        """ 
        The data is extracted from the IOGP CO2 storage projects database, 
        which is a CSV file containing information about 
        existing carbon storage projects in Europe.

        We allocate all icelandic storage projects to Norway, 
        as we don't have a separate country in the model for Iceland.
        """
        oil_extr = pd.read_excel(self.path,
                                         sheet_name="Oil Production - Tonnes",header=2)
        gas_extr = pd.read_excel(self.path,
                                       sheet_name="Gas Production - EJ",header=2)
        oil_extr["Country"] = convert_country_names(
            oil_extr["Million tonnes"])
        oil_extr = oil_extr[
            oil_extr["Country"].notnull()].set_index("Country")

        gas_extr["Country"] = convert_country_names(gas_extr["Exajoules"])
        gas_extr = gas_extr[
            gas_extr["Country"].notnull()].set_index("Country")
        
        # only keep columns that can be converted to int
        oil_extr = oil_extr[
            [c for c in oil_extr.columns if isinstance(c, int)]]
        gas_extr = gas_extr[
            [c for c in gas_extr.columns if isinstance(c, int)]]
        # convert oil from Million tonnes to bt
        oil_extr = oil_extr / self.DENSITY_OIL
        # convert gas from EJ to bt
        gas_extr = gas_extr / self.BKGNG2EJ / self.DENSITY_NATURAL_GAS
        # common years
        common_years = oil_extr.columns.intersection(gas_extr.columns)
        oil_extr = oil_extr[common_years]
        gas_extr = gas_extr[common_years]
        extr = gas_extr.add(oil_extr,fill_value=0) * self.DENSITY_CO2
        # to ktCO2eq/hour
        extr /= (8760 / 1000)
        potential_capacity = extr.iloc[:,-1]

        return potential_capacity

    # -------- methods ------------------------    
    def get_capacity_limit(self) -> Attribute:
        """
        Returns the limit on carbon storage capacity from oil and gas production.
        """
        data = self.data
        data.name = "capacity_limit"
        return Attribute(
            name="capacity_limit",
            default_value=0,
            df=data,
            unit="tCO2/h",
            source=SourceInformation(
                description=(
                    "The limit on carbon storage capacity is based on historic "
                    "oil and gas production data. The idea is that the injection "
                    "capacity of CO2 storage is limited by the amount of oil and gas "
                    "that has been extracted, as the storage sites are often located "
                    "in depleted oil and gas fields. The dataset uses the "
                    "Energy Institute's data on oil and gas extraction to "
                    "estimate the potential CO2 storage capacity in Europe."
                ),
                metadata=self.metadata,
            )
        )

