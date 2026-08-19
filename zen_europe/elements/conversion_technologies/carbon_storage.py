from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.financial.ECB import ECBInflation
from zen_europe.datasets.datasets.technology.CO2_storage_costs_ZEP import CO2StorageCostsZEP
from zen_europe.datasets.datasets.technology.IOGP_carbon_storage_projects import IOGPCarbonStorageProjects
from zen_europe.datasets.datasets.technology.energyinst_carbon_storage_limit import OGExtractionCarbonStorageLimit
from zen_europe.datasets.datasets.technology.northern_lights_costs import NorthernLightsCosts

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, SourceInformation


class CarbonStorage(ConversionTechnology):
    """Class containing all data and assumptions for carbon (CO2) storage."""

    name: str = "carbon_storage"

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of carbon storage to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of carbon storage to carbon.
        """
        return Attribute(name="input_carrier", default_value=["carbon"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of carbon storage to an empty list.

        Carbon storage has no output carrier: captured carbon is permanently
        stored, not converted into another dependent carrier.
        """
        return Attribute(name="output_carrier", default_value=[], element=self)

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of carbon storage.

        """
        zep_costs = CO2StorageCostsZEP(source_path=self.source_path)
        return zep_costs.get_lifetime()

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of carbon storage.

        """
        if self.settings.investment.use_construction_times:
            nl_costs = NorthernLightsCosts(source_path=self.source_path)
            return nl_costs.get_construction_time()
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of carbon storage.

        Carbon storage has no dependent carrier (input carrier = output carrier
        = carbon), so the conversion factor is left empty.
        """
        attr = self.conversion_factor
        cf = []
        attr.set_data(
            default_value=cf,
            source=AssumptionInformation(
                description=(
                    "The conversion factor of carbon storage is manually set "
                    "to an empty list, as carbon storage has no dependent "
                    "carrier (input carrier = output carrier = carbon)."
                ),
            ),
        )
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific conversion capital expenditure (capex) for carbon
        storage.

        Returns:
            Attribute: An Attribute object containing the specific conversion capex data.
        """
        nl_costs = NorthernLightsCosts(source_path=self.source_path)
        specific_capex = nl_costs.get_capex_specific()
        ecb_inflation = ECBInflation(source_path=self.source_path)
        inflation = ecb_inflation.get_inflation_rate(
            base_year=NorthernLightsCosts.MONEY_YEAR,
            target_year=self.settings.time.reference_year,
        )
        specific_capex = specific_capex * inflation
        attr = self.capex_specific_conversion
        attr.set_data(
            default_value=specific_capex,
            unit="Euro/tCO2",
            source=SourceInformation(
                description=(
                    "The specific conversion capex of carbon storage is "
                    "obtained from the Northern Lights costs dataset."
                ),
                metadata=nl_costs.metadata,
            ),
        )
        return attr
    
    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for carbon
        storage.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        zep_costs = CO2StorageCostsZEP(source_path=self.source_path)
        opex = zep_costs.get_opex_specific_variable()
        ecb_inflation = ECBInflation(source_path=self.source_path)
        inflation = ecb_inflation.get_inflation_rate(
            base_year=CO2StorageCostsZEP.MONEY_YEAR,
            target_year=self.settings.time.reference_year,
        )
        opex_data = opex.default_value * inflation
        opex.set_data(
            default_value=opex_data,
            source=opex.sources[-1])
        return opex

    def _set_carbon_intensity_technology(self) -> Attribute:
        """
        Sets the carbon intensity of carbon storage.

        Returns:
            Attribute: An Attribute object containing the carbon intensity data.
        """
        attr = self.carbon_intensity_technology
        attr.set_data(
            default_value=-1,
            unit="ton/tCO2",
            source=AssumptionInformation(
                description=(
                    "The carbon intensity of carbon storage is manually set "
                    "to -1, crediting one unit of permanently stored CO2 per "
                    "unit of carbon processed."
                ),
            ),
        )
        return attr

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of carbon storage.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        if self.settings.investment.use_existing_capacities:
            igop_projects = IOGPCarbonStorageProjects(source_path=self.source_path)
            return igop_projects.get_capacity_existing()
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
        Sets the capacity limit of carbon storage.

        Returns:
            Attribute: An Attribute object containing the capacity limit data.
        """
        if self.settings.investment.allow_investment:
            if self.settings.data_source.use_OG_carbon_storage_limit:
                OG_extraction_db = OGExtractionCarbonStorageLimit(
                    source_path=self.source_path)
                return OG_extraction_db.get_capacity_limit()
            else:
                data = self.capacity_existing.df.groupby("node").sum()
                data.name = "capacity_limit"
                return Attribute(
                    name="capacity_limit",
                    default_value=0,
                    df=data,
                    unit="tCO2/h",
                    source=SourceInformation(
                        description=(
                            "The limit on carbon storage capacity is based on the "
                            "existing capacity from the IOGP report, which includes "
                            "all planned and under construction projects. "
                        ),
                        metadata=self.capacity_existing.sources[-1],
                    ),
                )
        else:
            return self.capacity_limit
