from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.technology_cost_database import TechnologyCostDatabase
from zen_europe.datasets.datasets.financial.dea import DEA

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, ConversionTechnology, SourceInformation


class Pyrolysis(ConversionTechnology):
    """Class containing all data and assumptions for slow pyrolysis of
    biomass (to hard coal / biochar, oil and district heat)."""

    name: str = "pyrolysis"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of pyrolysis to oil.
        """
        return Attribute(
            name="reference_carrier", default_value=["oil"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of pyrolysis to biomass and electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["biomass", "electricity"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of pyrolysis to hard coal, district heat and
        oil.
        """
        return Attribute(
            name="output_carrier",
            default_value=["hard_coal", "district_heat", "oil"],
            element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of pyrolysis.

        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_lifetime(self)

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of pyrolysis.

        Values from the DEA technology catalogue for renewable fuels (Large
        scale slow pyrolysis (20 MW), straw feedstock), normalized to the
        oil reference carrier (biochar/pyrolysis-oil producing process:
        0.99 MWh biomass input, 0.04 MWh electricity, 0.22 MWh oil and
        0.05 MWh district heat, plus 0.4 MWh-equivalent hard coal/biochar
        output, all per MWh of biomass processed).
        https://ens.dk/en/our-services/projections-and-models/technology-data/technology-data-renewable-fuels
        """
        attr = self.conversion_factor
        dea_dataset = DEA(source_path=self.source_path)
        cf = dea_dataset.get_conversion_factor_pyrolysis()
        source = SourceInformation(
            description=(
                "The conversion factor of pyrolysis is a manually derived "
                "value based on the DEA technology catalogue for renewable "
                "fuels (Large scale slow pyrolysis, straw feedstock), "
                "normalized to the oil reference carrier."
            ),
            metadata=dea_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of pyrolysis.

        """
        if self.settings.investment.use_construction_times:
            tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
            return tech_db.get_construction_time(self)
        else:
            return self.construction_time

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for pyrolysis.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        tech_db = TechnologyCostDatabase(
                    settings=self.settings, source_path=self.source_path)
        return tech_db.get_capex_specific_conversion(self)

    def _set_opex_specific_fixed(self) -> Attribute:
        """
        Sets the specific fixed operational expenditure (opex) for
        pyrolysis.

        Returns:
            Attribute: An Attribute object containing the specific fixed opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_fixed(self)

    def _set_opex_specific_variable(self) -> Attribute:
        """
        Sets the specific variable operational expenditure (opex) for
        pyrolysis.

        Returns:
            Attribute: An Attribute object containing the specific variable opex data.
        """
        tech_db = TechnologyCostDatabase(
            settings=self.settings, source_path=self.source_path)
        return tech_db.get_opex_specific_variable(self)

    # TODO: capacity_existing should be sourced from a biochar-production
    # tracker ("biochar_existing.xlsx" in the legacy pipeline), which is not
    # yet implemented as a dataset in zen_europe; framework default applies.
