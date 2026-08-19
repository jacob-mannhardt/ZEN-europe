from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.carrier.aidres import Aidres
from zen_europe.datasets.datasets.carrier.eurostat import Eurostat

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology, SourceInformation


class OlefinFromNaphtha(ConversionTechnology):
    """Class containing all data and assumptions for olefin production
    from naphtha."""

    name: str = "olefin_from_naphtha"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of olefin from naphtha to olefin.
        """
        return Attribute(
            name="reference_carrier", default_value=["olefin"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of olefin from naphtha to naphtha and
        electricity.
        """
        return Attribute(
            name="input_carrier", default_value=["naphtha", "electricity"],
            element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of olefin from naphtha to olefin.
        """
        return Attribute(
            name="output_carrier", default_value=["olefin"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of olefin from naphtha.

        """
        attr = self.lifetime
        attr.set_data(
            default_value=25,
            source=AssumptionInformation(
                description=(
                    "The lifetime of olefin from naphtha is manually set "
                    "to 25 years, assuming a standard industrial technology "
                    "lifetime."
                ),
            ),
        )
        return attr

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of olefin from naphtha.

        """
        if self.settings.investment.use_construction_times:
            attr = self.construction_time
            attr.set_data(
                default_value=3,
                source=AssumptionInformation(
                    description=(
                        "The construction time of olefin from naphtha is "
                        "manually set to 3 years, assuming a standard "
                        "industrial construction timeline."
                    ),
                ),
            )
            return attr
        else:
            return self.construction_time

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of olefin from naphtha.

        """
        attr = self.conversion_factor
        aidres_dataset = Aidres(source_path=self.source_path)
        cf_dict = aidres_dataset.get_conversion_factors_aidres(self.name)
        cf = [
            {carrier: {"default_value": value, "unit": "GWh/tonproduct"}}
            for carrier, value in cf_dict.items()
        ]
        source = SourceInformation(
            description=(
                "The conversion factor of olefin from naphtha is obtained "
                "from the Aidres dataset (Table 32, naphtha-to-olefin route)."
            ),
            metadata=aidres_dataset.metadata,
        )
        attr.set_data(default_value=cf, source=source)
        return attr

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity for olefin from naphtha.

        Derived from Eurostat naphtha demand, divided by the naphtha
        conversion factor to obtain an equivalent olefin production capacity.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        if self.settings.investment.use_existing_capacities:
            eurostat_dataset = Eurostat(settings=self.settings, source_path=self.source_path)
            naphtha_demand = eurostat_dataset.get_naphtha_demand()
            common_nodes = naphtha_demand.index.intersection(
                self.model.config.system.set_nodes)
            demand = naphtha_demand.loc[common_nodes, eurostat_dataset.eurostat_year] / 8760
            naphtha2olefin = self.conversion_factor.default_value
            naphtha_cf = next(
                entry["naphtha"]["default_value"]
                for entry in naphtha2olefin if "naphtha" in entry)
            capacity_existing = demand / naphtha_cf
            capacity_existing.index.name = "node"
            capacity_existing.name = "capacity_existing"
            attr = self.capacity_existing
            source = SourceInformation(
                description=(
                    "The existing capacity of olefin from naphtha is derived "
                    "from the Eurostat naphtha demand, divided by the naphtha "
                    "conversion factor, assuming that all naphtha demand is "
                    "currently converted to olefins."
                ),
                metadata=eurostat_dataset.metadata,
            )
            attr.set_data(df=capacity_existing, source=source, unit="tonproduct/hour")
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

    # TODO: capex_specific_conversion/opex_specific_fixed should be sourced
    # from the curated "costs_additional_technologies.xlsx" (AddTech)
    # dataset, which is not yet implemented in zen_europe; framework
    # defaults apply.
