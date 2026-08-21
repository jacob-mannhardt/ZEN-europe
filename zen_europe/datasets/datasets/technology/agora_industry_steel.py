from __future__ import annotations

from inspect import Attribute
from pathlib import Path

from zen_creator import ConversionTechnology, SourceInformation
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

import pandas as pd

from zen_europe.datasets.datasets.carrier.ipcc_emission_factors import IPCCEmissionFactors
from zen_europe.datasets.datasets.financial.ECB import ECBDollar2Euro, ECBInflation
from zen_europe.utils.constants import Constants

class AgoraIndustrySteel(Dataset[pd.DataFrame]):
    """
    Dataset class for the steel production technology from Agora Industry.

    """

    name = "agora_industry_steel"

    MONEY_YEAR = 2024

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "Low-carbon technologies for the global steel transformation"
            ),
            author=["Wido K. Witecka"
                    "Julian Somers"
                    "Kathy Reimann"
                    "Niklas Wagner"
                    "Ole Zelt"
                    "Alexander Jülich"
                    "Clemens Schneider"
                    "Prof. Max Åhman"],
            publication="Agora Industry",
            publication_year=2024,
            url="https://www.agora-industry.org/publications/low-carbon-technologies-for-the-global-steel-transformation",             
        )

    def _set_path(self) -> Path | None:
        if self.source_path is None:
            raise ValueError("source_path must be set to load the dataset.")
        return self.source_path

    def _set_data(self) -> dict[str, pd.Series]:
        """ 
        No data to be set
        """
        data = {}
        
        data = pd.Series(data)
        return data

    # -------- methods ------------------------    
    def get_opex_specific_variable(self, element: ConversionTechnology) -> Attribute:
        """
        Get the specific variable operational expenditure (opex) for the steel production technology.

        The size and energy use values are taken from Agora Industry's 
        Low-carbon technologies for the global steel transformation.

        We use the average values for the variable opex. We add the operating costs
        to the variable opex

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        opex_specific_variable = {
            # from the BF_BOF-CCS p. 65
            "BF_BOF": 197+(109+78)/2 + 33, 
            # NG-DRI CCS, p. 59
            "NG_DRI": 261 + (108+78)/2 + 33,  
            # H2-DR EAF, p. 55
            "H2_DRI": 264 + (108+78)/2 + 33,  
            # EAF, p. 69
            "EAF": (453+628)/2 + 33,
        }

        fixed_opex = {
            "BF_BOF": 69,
            "NG_DRI": 59,
            "H2_DRI": 59,
            "EAF": 45,
        }
        assert element.name in opex_specific_variable, (f"Element {element.name} not found "
        "in opex_specific_variable.")
        opex = opex_specific_variable[element.name] + fixed_opex[element.name]
        inflation_dataset = ECBInflation(self.source_path)
        inflation = inflation_dataset.get_inflation_rate(
            base_year=self.MONEY_YEAR,
            target_year=element.settings.time.reference_year
        )
        dollar2euro = ECBDollar2Euro(self.source_path).get_dollar2euro(
            year=self.MONEY_YEAR)
        opex = opex * inflation * dollar2euro
        attr = element.opex_specific_variable

        attr.set_data(
            default_value=opex,
            unit="Euro/tonproduct",
            source=SourceInformation(
                description=(
                    "The specific variable opex for steel production technologies is derived from "
                    "Agora Industry (2021), 'Low-carbon technologies for "
                    "the global steel transformation'"
                ),
                metadata=self.metadata,
            ),
        )
        return attr

    def get_lifetime(self, element: ConversionTechnology) -> Attribute:
        """
        Get the lifetime of steel production technologies.

        We assume the average lifetime between the financial lifetime (18 years, from
        https://www.agora-industry.org/data-tools/steel-transformation-cost-calculator#downloads) and
        the technical lifetime (50 years, p. 46)

        Returns:
            Attribute: An Attribute object containing the lifetime data.
        """
        lifetime = (50 + 18) / 2 # years
        attr = element.lifetime
        attr.set_data(
            default_value=lifetime,
            unit="1",
            source=SourceInformation(
                description=(
                    "The lifetime of steel production technologies is derived as the average "
                    "of the financial and technical lifetimes assumed in "
                    "Agora Industry (2021), 'Low-carbon technologies for the "
                    "global steel transformation'."
                ),
                metadata=self.metadata,
            ),
        )
        return attr

    def _get_raw_conversion_factor(
            self, element: ConversionTechnology) -> dict[str, float]:
        """
        Get the raw conversion factor of steel production technologies.
        """
        conversion_factor = {
            "BF_BOF": {
                "hard_coal": (14.8 + 4.7)}, # GJ/tonproduct
            "NG_DRI": {
                "natural_gas": 10.5,
                "electricity": (0.25 + 1.24),
                "hard_coal": 0.07}, # GJ/tonproduct
            "H2_DRI": {
                "hydrogen": 8.25,
                "electricity": (0.29 + 1.77),
                "hard_coal": 0.53}, # GJ/tonproduct
            "EAF": {
                "electricity": 2.46,
                "hard_coal": 0.37}, # GJ/tonproduct
        }
        assert element.name in conversion_factor, (f"Element {element.name} not found"
        "in conversion_factor.")
        data = conversion_factor[element.name]
        for carrier, value in data.items():
            data[carrier] = value / (Constants.GJ_PER_MWH * 1000) # convert GJ to GWh
        return data
    
    def get_conversion_factor(self, element: ConversionTechnology) -> Attribute:
        """
        Get the conversion factor of steel production technologies.
        The flows are taken from the different steel production technologies and 
        their flow charts
        """
        data = self._get_raw_conversion_factor(element)
        attr = element.conversion_factor
        attr.set_data(
            default_value=[{carrier: {"default_value": value, "unit": "GWh/tonproduct"}}
                           for carrier, value in data.items()],
            source=SourceInformation(
                description=(
                    "The conversion factor of steel production technologies is derived from "
                    "Agora Industry (2021), 'Low-carbon technologies for the "
                    "global steel transformation'."
                ),
                metadata=self.metadata,
            ),
        )
        return attr

    def get_carbon_intensity_technology(self, element: ConversionTechnology) -> Attribute:
        """
        Get the carbon intensity of steel production technologies.

        The carbon intensity is derived from the process emissions 
        (from the reduction reaction, sintering, coking
        and lime production) net of the emissions already attributed to 
        hard coal combustion via its carrier-level
        carbon intensity, based on Agora Industry (2021), 
        'Low-carbon technologies for the global steel transformation'.

        Returns:
            Attribute: An Attribute object containing the carbon intensity data.
        """
        attr = element.carbon_intensity_technology
        total_emissions = { # ton/tproduct
            "BF_BOF": 0.28 + 0.93 + 0.4 + 0.08 + 0.18,
            "NG_DRI": 0.35 + 0.04 + 0.17,
            "H2_DRI": 0.01,
            "EAF": 0.01,
        }
        # it is assumed that H2-DRI and EAF use charcoal (carbon neutral)
        # so the 0.01 t/tproduct is the emissions are from the process, not the fuel.
        carrier_exemption = {
            "BF_BOF": [],
            "NG_DRI": [],
            "H2_DRI": ["hard_coal"],
            "EAF": ["hard_coal"],}
        assert element.name in total_emissions, (f"Element {element.name} not found"
        "in total_emissions.")
        conversion_factor = self._get_raw_conversion_factor(element)
        ipcc_emission_factor = IPCCEmissionFactors(self.source_path)
        feedstock_emissions = 0.0
        for carrier, value in conversion_factor.items():
            if carrier in carrier_exemption[element.name]:
                continue
            carrier_element = element.model.carriers[carrier]
            if carrier in ipcc_emission_factor.data:
                carrier_carbon_intensity = ipcc_emission_factor.data[carrier] # tons/MWh
            else:
                continue
            feedstock_emissions += value * carrier_carbon_intensity * 1000

        process_emissions = total_emissions[element.name] - feedstock_emissions
        attr.set_data(
            default_value=process_emissions,
            unit="ton/tonproduct",
            source=SourceInformation(
                description=(
                    "The carbon intensity of steel production technologies is derived "
                    "from Agora Industry (2021), 'Low-carbon technologies for the "
                    "global steel transformation' with emission factors from "
                    "the IPCC emission factors dataset."
                ),
                metadata=self.metadata,
            ),
        )
        return attr