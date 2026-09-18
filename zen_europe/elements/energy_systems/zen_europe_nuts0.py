from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator.model import Model

import numpy as np
from zen_creator import AssumptionInformation, Attribute, EnergySystem

from zen_europe.datasets.dataset_collections.edges import Edges
from zen_europe.datasets.datasets.energy_system.nuts_shp import NUTSshp
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)


class EnergySystemNuts0(EnergySystem):
    """Nuts0 energy system for Europe, with nodes based on NUTS0 regions
    and edges based on adjacency of NUTS regions and TYNDP data.
    """

    name: str = "energy_system_nuts0"

    # penalty price for emitting more than the carbon budget or the annual
    # limit allow
    PRICE_CARBON_EMISSIONS_OVERSHOOT = 5000

    def __init__(self, model: Model):
        super().__init__(model=model)

    def _set_set_nodes(self) -> Attribute:
        attr = NUTSshp(source_path=self.source_path).get_set_nodes(self)
        return attr

    def _set_set_edges(self) -> Attribute:
        attr = Edges(source_path=self.source_path).get_set_edges(self)

        # check that edges are not empty
        if (set_edges := attr.df) is None or set_edges.empty:
            raise ValueError("No edges are set in the energy system.")

        # manual connections NO-BE and NO-FR for gas, and SE-LT for electricity
        set_edges.loc["NO-FR", :] = ["NO", "FR"]
        set_edges.loc["FR-NO", :] = ["FR", "NO"]
        set_edges.loc["NO-BE", :] = ["NO", "BE"]
        set_edges.loc["BE-NO", :] = ["BE", "NO"]
        set_edges.loc["SE-LT", :] = ["SE", "LT"]
        set_edges.loc["LT-SE", :] = ["LT", "SE"]
        attr.set_data(
            df=set_edges.drop_duplicates().sort_index(),
            source=AssumptionInformation(
                description=(
                    "The connections NO-BE and NO-FR for gas, and SE-LT for "
                    "electricity, are added manually."
                ),
            ),
        )

        # write csv
        return attr

    def _set_knowledge_depreciation_rate(self) -> Attribute:
        """
        Sets the knowledge depreciation rate of the energy system.
        """
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_knowledge_depreciation_rate(self)

    def _set_knowledge_spillover_rate(self) -> Attribute:
        """
        Sets the knowledge spillover rate between the nodes.
        """
        attr = self.knowledge_spillover_rate
        if self.settings.investment.use_inf_spillover_rate:
            return attr.set_data(
                default_value=np.inf,
                unit="1",
                source=AssumptionInformation(
                    description=(
                        "The knowledge spillover rate between the nodes is "
                        "infinite, so that knowledge is shared without any "
                        "loss between the nodes."
                    ),
                ),
            )
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_knowledge_spillover_rate(self)

    def _set_market_share_unbounded(self) -> Attribute:
        """
        Sets the market share that is exempt from the diffusion limit.
        """
        attr = self.market_share_unbounded
        if not self.settings.investment.use_unbounded_market_share:
            return attr.set_data(
                default_value=0,
                unit="1",
                source=AssumptionInformation(
                    description=(
                        "No market share is exempt from the diffusion limit."
                    ),
                ),
            )
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_market_share_unbounded(self)

    def _set_price_carbon_emissions_budget_overshoot(self) -> Attribute:
        """
        Sets the penalty price for overshooting the carbon budget.
        """
        attr = self.price_carbon_emissions_budget_overshoot
        return attr.set_data(
            default_value=self.PRICE_CARBON_EMISSIONS_OVERSHOOT,
            unit="Euro/tons",
            source=AssumptionInformation(
                description=(
                    f"The penalty price for overshooting the carbon budget is "
                    f"manually set to "
                    f"{self.PRICE_CARBON_EMISSIONS_OVERSHOOT} Euro per ton, "
                    f"far above any abatement cost, so that the budget is only "
                    f"overshot if the model would be infeasible otherwise."
                ),
            ),
        )

    def _set_price_carbon_emissions_annual_overshoot(self) -> Attribute:
        """
        Sets the penalty price for overshooting the annual carbon limit.

        The annual limit can only be overshot if it is an emission trading cap
        or if overshooting is allowed explicitly.
        """
        attr = self.price_carbon_emissions_annual_overshoot
        if not (self.settings.emissions.use_EU_ETS_cap
                or self.settings.emissions.use_annual_limit_overshoot):
            return attr.set_data(
                default_value=np.inf,
                unit="Euro/tons",
                source=AssumptionInformation(
                    description=(
                        "The annual carbon emissions limit cannot be overshot."
                    ),
                ),
            )
        return attr.set_data(
            default_value=self.PRICE_CARBON_EMISSIONS_OVERSHOOT,
            unit="Euro/tons",
            source=AssumptionInformation(
                description=(
                    f"The penalty price for overshooting the annual carbon "
                    f"emissions limit is manually set to "
                    f"{self.PRICE_CARBON_EMISSIONS_OVERSHOOT} Euro per ton, "
                    f"far above any abatement cost, so that the limit is only "
                    f"overshot if the model would be infeasible otherwise."
                ),
            ),
        )

    # ---------- Attributes that still have to be ported ----------

    # NOTE: price_carbon_emissions (0 Euro/tons),
    # carbon_emissions_cumulative_existing (0 gigatons) and the discount rate
    # (0.05, cited in ZEN-creator) equal the values of the legacy pipeline, so
    # they are left at the default of the framework.

    # TODO: carbon_emissions_budget is the remaining European carbon budget of
    # the modeled sectors, gated by emissions.use_carbon_budget. The legacy
    # pipeline derives it from the IPCC remaining budget for
    # emissions.temperature_increase at emissions.probability_carbon_budget,
    # minus the global emissions since 2020, times a European share (equal per
    # capita by default, with grandfathering, responsibility, ability to pay
    # and human rights as alternatives), times the share of the modeled
    # sectors in the European emissions. None of the underlying data (IPCC
    # budgets, historical global emissions, population, EEA emissions per
    # sector) is in data/raw_data, so the budget is infinite for now. With
    # emissions.calculate_budget_from_ETS it is instead the sum of the annual
    # limits below.

    # TODO: carbon_emissions_annual_limit is the annual emission target,
    # gated by emissions.use_carbon_annual_limit, and needs the EU emission
    # trading cap (emissions.use_EU_ETS_cap, use_EU_ETS_cap_ETS1only,
    # use_adjusted_ETS_to_keep_carbon_budget) and the intermediate reduction
    # goals (emissions.use_intermediate_emission_goal), neither of which is in
    # data/raw_data. The limit is infinite for now, while the legacy pipeline
    # writes a trajectory that ends at net zero in the last year.

    # TODO: the energy_system section of data/config.yaml switches the yearly
    # interpolation off for "carbon_emissions_limit", while ZEN-garden reads
    # the parameter as "carbon_emissions_annual_limit". Once the limit above
    # is ported, the name has to be corrected, otherwise the trajectory is
    # interpolated between the optimization years.
