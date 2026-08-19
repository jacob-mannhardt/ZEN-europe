from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.financial.dea import DEA

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, RetrofittingTechnology, SourceInformation


class SMR_CCS(RetrofittingTechnology):
    """Class containing all data and assumptions for steam methane
    reforming (SMR) retrofitted with post-combustion carbon capture (CCS)."""

    name: str = "SMR_CCS"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of SMR CCS to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of SMR CCS to natural gas and electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["natural_gas", "electricity"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of SMR CCS to carbon.
        """
        return Attribute(
            name="output_carrier", default_value=["carbon"], element=self
        )

    def _set_retrofit_reference_carrier(self) -> Attribute:
        """
        Sets the retrofit reference carrier of SMR CCS to carbon.
        """
        return Attribute(
            name="retrofit_reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of SMR CCS.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_lifetime(self)

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of SMR CCS.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of SMR CCS.

        Values from the DEA technology catalogue for carbon capture,
        transport and storage (Post-combustion carbon capture retrofit -
        100 MW(th) WtE or biomass CHP plant, used as a proxy entry),
        assuming all heat demand for the capture process is supplied from
        natural gas.
        https://ens.dk/en/our-services/projections-and-models/technology-data/technology-data-carbon-capture-transport-and
        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_SMR_CCS()
        source = SourceInformation(
            description=(
                "The conversion factor of SMR CCS is a manually derived "
                "value based on the DEA technology catalogue for carbon "
                "capture, transport and storage (Post-combustion carbon "
                "capture retrofit - 100 MW(th) WtE or biomass CHP plant, "
                "used as a proxy entry, assuming all heat demand is "
                "supplied from natural gas)."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for SMR CCS.

        `take_delta_cost_from_base_tech` is `False` for this technology, so
        the cost-database value is used directly (absolute cost), matching
        the legacy pipeline.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for SMR CCS.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        SMR CCS.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    def _set_retrofit_flow_coupling_factor(self) -> Attribute:
        """
        Return the retrofit flow coupling factor of SMR CCS.

        TODO: In the legacy pipeline this is computed as
        `carbon_intensity_carrier_fuel["natural_gas"] *
        SMR_natural_gas_conversion_factor (1.2987) * capture_rate (0.9,
        https://ens.dk/en/our-services/projections-and-models/technology-data/technology-data-carbon-capture-transport-and)`,
        requiring cross-referencing the natural_gas Carrier's carbon
        intensity attribute. Left at the framework default (1.0) pending
        that implementation.
        """
        attr = self.retrofit_flow_coupling_factor
        return attr

    # TODO: capacity_existing should be sourced from the IOGP CCS database
    # (technologies present in the capture map), which is not yet
    # implemented as a dataset in zen_europe; framework default applies.
