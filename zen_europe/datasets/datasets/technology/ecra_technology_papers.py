from __future__ import annotations

from inspect import Attribute
from pathlib import Path

from zen_creator import ConversionTechnology, SourceInformation
from zen_creator.datasets.datasets.dataset import Dataset
from zen_creator.datasets.datasets.metadata import MetaData

import pandas as pd

from zen_europe.utils.constants import Constants

class ECRATechnologyPapers(Dataset[pd.DataFrame]):
    """
    Dataset class for the state of the art cement manufacturing technology data from 
    ECRA (European Cement Research Academy) technology papers.

    """

    name = "ecra_technology_papers"

    MONEY_YEAR = 2014

    def __init__(self, source_path: Path | str | None = None):
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title=(
                "THE ECRA TECHNOLOGY PAPERS 2022 - State of the Art Cement Manufacturing"
            ),
            author=["ECRA (European Cement Research Academy)"],
            publication="ECRA Technology Papers",
            publication_year=2022,
            url="https://www.ecra-online.org/research/technology-papers",
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
    def get_capex_specific_retrofitting(self,element: ConversionTechnology) -> Attribute:
        """
        Get the specific capital expenditure (CAPEX) for the retrofitting
        of cement kilns to other feedstocks.

        The size and energy use values are taken from Annex II, p. 185. 
        The substitution to biomass and waste is taken from Technology Paper 14,
        with the highest value (15 Mio Euro) used for the retrofitting to biomass
        because of the problems with high substitution rates of biomass. 
        The retrofitting to waste is assumed to be lower (10 Mio Euro, average value).
        The substitution to hydrogen is taken from Technology paper 18, 
        assuming the highest value of 4.5 Mio Euro for the retrofitting to hydrogen.
        TODO this is not for a 100% substitution, but for a 10% substitution, so
        we need to rework the x_to_cement_fuel technologies
        Returns:
            Attribute: An Attribute object containing the specific CAPEX data.
        """
        attr = element.capex_specific_conversion
        energy_use = 3.352 / Constants.SECONDS_PER_HOUR # GWh/tproduct
        size = 2*1e6/Constants.HOURS_PER_YEAR*energy_use # t/a -> t/h -> GW 
        specific_capex = {
            "biomass_to_cement_fuel": 15e6/size,
            "waste_to_cement_fuel": 10e6/size,
            "hydrogen_to_cement_fuel": 4.5e6/size,
        }
        if element.name not in specific_capex:
            raise ValueError(
                f"Specific CAPEX for retrofitting to {element.name} is not defined."
            )
        else:
            attr.set_data(
                default_value=specific_capex[element.name],
                source=SourceInformation(
                    description=(
                        "The specific CAPEX for retrofitting cement kilns to other feedstocks "
                        "is derived from ECRA (2022), Technology Papers 2022."
                        "The size and energy use values are taken from Annex II, p. 185. "
                        "The substitution to biomass and waste is taken from Technology Paper 14,"
                        "with the highest value (15 Mio Euro) used for the retrofitting to biomass"
                        "because of the problems with high substitution rates of biomass. "
                        "The retrofitting to waste is assumed to be lower (10 Mio Euro, average value)."
                        "The substitution to hydrogen is taken from Technology paper 18, "
                        "assuming the highest value of 4.5 Mio Euro for the retrofitting to hydrogen."
                    ),
                    metadata=self.metadata,
                ),
                unit="Euro/GW",
            )
        return attr
    