from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.financial.ECB import ECBDollar2Euro, ECBInflation
from zen_europe.datasets.datasets.technology.gie_lng_map import GIELNGMap

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, MetaData, SourceInformation
import numpy as np

from zen_europe.utils.constants import Constants

class LNGTerminal(ConversionTechnology):
    """Class containing all data and assumptions for LNG terminals (regasification)."""

    name: str = "lng_terminal"

    BCM2GWH = Constants.NATURAL_GAS_GWH_PER_BCM # bcm to GWh conversion factor

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of LNG terminals to natural gas.
        """
        return Attribute(
            name="reference_carrier", default_value=["natural_gas"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of LNG terminals to LNG.
        """
        return Attribute(name="input_carrier", default_value=["lng"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of LNG terminals to natural gas.
        """
        return Attribute(
            name="output_carrier", default_value=["natural_gas"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of LNG terminals.

        """
        attr = self.lifetime
        attr.set_data(
            default_value=30,
            source=SourceInformation(
                description=(
                    "The lifetime of LNG terminals is "
                    "based on Brauers et al. (2021) (p. 13)."
                ),
                metadata=MetaData(
                    name="lng_brauers",
                    title=(
                        "Liquefied natural gas expansion plans in Germany: "
                        "The risk of gas lock-in under energy transitions"
                    ),
                    author=["Hanna Brauers", "Isabell Braunger", "Jessice Jewell"],
                    publication="Energy Research & Social Science",
                    publication_year=2021,
                    doi="https://doi.org/10.1016/j.erss.2021.102059",
                )
            ),
        )
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of LNG terminals.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            attr.set_data(
                default_value=4,
                source=SourceInformation(
                    description=(
                        "The construction time of LNG terminals is set to "
                        "4 years, based on the typical construction time of LNG "
                        "import terminals reported in the industry literature."
                    ),
                    metadata=MetaData(
                        name="lng_construction_time",
                        title="Are LNG liquefication projects taking longer to construct?",
                        author=["Tom Zeal"],
                        publication="LNG 2019",
                        publication_year=2019,
                        url="https://www.almendron.com/tribuna/wp-content/uploads/2022/05/40-lng19-04april2019-zeal-tom-paper.pdf"
                    )
                ),
            )
            return attr
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of LNG terminals.

        Regasification is assumed to be lossless (1 unit of LNG produces 1 unit
        of natural gas).
        """
        attr = self.conversion_factor
        cf = [{"lng": {"default_value": 1, "unit": "GWh/GWh"}}]
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of LNG terminals is manually set to 1, "
                    "assuming lossless regasification of LNG to natural gas."
                ),
            ),
        )
        return attr

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for LNG terminals.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        attr = self.opex_specific_variable
        vopex = 0.5/0.293 # regasification cost of 0.5 $/MMBtu converted to $/MWh, 1 MMBtu = 0.293 MWh
        ecb_d2e = ECBDollar2Euro(source_path=self.source_path)
        vopex = vopex * ecb_d2e.get_dollar2euro(2018)
        inflation = ECBInflation(source_path=self.source_path)
        vopex = vopex * inflation.get_inflation_rate(2018, 
                                                     self.settings.time.reference_year)
        attr.set_data(
            default_value=vopex,
            unit="Euro/MWh",
            source=SourceInformation(
                description=(
                    "The variable opex of LNG terminals is set to the "
                    "regasification cost of 0.5 $/MMBtu, converted to Euro/MWh."
                ),
                metadata=MetaData(
                    name="lng_vopex",
                    title="The Open LNG Regasification Model: A Manual",
                    author=["Perrine Toledano", 
                            "Nicolas Maennling", 
                            "Thomas Mitro", 
                            "Felipe Botelho Tavares"],
                    publication="CCSI",
                    publication_year=2018,
                    url="https://www.researchgate.net/publication/329641146_Manual_for_the_Open_LNG_Regasification_Model?__cf_chl_tk=5U8nxvr0CS5UxSUazBB.8kBhGxlk1iLuMOM.vXxM27w-1787052634-1.0.1.1-3YhBlzA1f1al4nUPoOl8oK7miENXdI1w37nxWfoRv4Q"
                )
            ),
        )
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for LNG terminals.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        attr = self.capex_specific_conversion
        capex_total = 500*1e6 # Brunsbüttel LNG terminal
        capacity = 8 # bcm
        capacity = capacity * self.BCM2GWH / Constants.HOURS_PER_YEAR * 1e6 # convert to kW
        capex_specific = capex_total / capacity # Euro/kW
        inflation = ECBInflation(source_path=self.source_path)
        capex_specific = (capex_specific * 
                          inflation.get_inflation_rate(2021,
                          self.settings.time.reference_year))

        attr.set_data(
            default_value=capex_specific,
            unit="Euro/kW",
            source=SourceInformation(
                description=(
                    "The specific capital expenditure of LNG terminals is "
                    "based on the Brunsbüttel LNG terminal data."
                ),
                metadata=MetaData(
                    name="lng_brauers",
                    title=(
                        "Liquefied natural gas expansion plans in Germany: "
                        "The risk of gas lock-in under energy transitions"
                    ),
                    author=["Hanna Brauers", "Isabell Braunger", "Jessice Jewell"],
                    publication="Energy Research & Social Science",
                    publication_year=2021,
                    doi="https://doi.org/10.1016/j.erss.2021.102059",
                )
            ),
        )
        return attr
    
    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity for LNG terminals.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        if self.settings.investment.use_existing_capacities:
            gie_lng_map = GIELNGMap(source_path=self.source_path)
            capacity_existing = gie_lng_map._calculate_capacity_existing_lng(self)
            attr = self.capacity_existing
            source = SourceInformation(
                description=(
                    "The existing capacity of LNG terminals is derived from the "
                    "SciGRID GIE dataset of LNG terminal storage-to-pipeline "
                    "send-out capacities."
                ),
                metadata=gie_lng_map.metadata,
            )
            attr.set_data(
                df=capacity_existing, source=source, unit="GW")
            return attr
        else:
            attr = self.capacity_existing
            attr.set_data(
                default_value=0,
                df=None,
                source=AssumptionInformation(
                    description=(
                        "We do not consider existing capacities."
                    ),
                ),
            )
            return attr

    def _set_capacity_limit(self) -> Attribute:
        """
        Sets the capacity limit for LNG terminals.

        The capacity limit is computed as the existing capacity multiplied by
        the TYNDP 2022 LNG potential-increase factor.

        Returns:
            Attribute: An Attribute object containing the capacity limit data.
        """
        attr = self.capacity_limit
        if not self.settings.investment.allow_investment:
            attr.set_data(
                default_value=0,
                source=AssumptionInformation(
                    description=(
                        "The capacity limit is set to 0, "
                        "as investment is not allowed."
                    ),
                ),
            )
        else:
            data = self.capacity_existing.df
            capacity_limit = data.groupby(level=0).sum()
            capacity_limit.loc[:] = np.inf
            capacity_limit.name = "capacity_limit"
            attr.set_data(
                df=capacity_limit,
                default_value=0,
                source=AssumptionInformation(
                    description=(
                        "Assume infinite capacity limit for those countries "
                        "with existing lng terminals."
                    ),
                ),
                unit="GW",
            )
        return attr
