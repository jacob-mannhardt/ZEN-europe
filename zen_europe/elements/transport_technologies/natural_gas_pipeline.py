from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation, MetaData
from zen_creator.elements import TransportTechnology
from zen_creator.utils.attribute import Attribute, SourceInformation

# The pipeline investment cost is taken from the TYNDP 2022 scenario building
# guidelines (Tab. 14, p. 32).
TYNDP_SCENARIO_GUIDELINES = MetaData(
    name="tyndp_2022_scenario_building_guidelines",
    title="TYNDP 2022 Scenario Building Guidelines",
    author=["ENTSOG", "ENTSO-E"],
    publication="ENTSOG and ENTSO-E",
    publication_year=2021,
    url=(
        "https://www.entsog.eu/sites/default/files/2021-10/"
        "entsos_TYNDP_2022_Scenario_Building_Guidelines_211007_1.pdf"
    ),
)


class NaturalGasPipeline(TransportTechnology):
    """Class containing all data and assumptions for natural gas pipeline
    transport technology."""

    name: str = "natural_gas_pipeline"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of natural gas pipeline to natural gas.
        """
        return Attribute(
            name="reference_carrier", default_value=["natural_gas"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of natural gas pipeline.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=60,
            source=AssumptionInformation(
                description=(
                    "The lifetime of natural gas pipelines is manually set to "
                    "60 years, in line with the lifetime of the other linear "
                    "transport infrastructure."
                ),
            ),
        )

    def _set_transport_loss_factor_linear(self) -> Attribute:
        """
        Sets the linear transport loss factor of natural gas pipeline.
        """
        attr = self.transport_loss_factor_linear
        return attr.set_data(
            default_value=5e-5,
            unit="1/km",
            source=AssumptionInformation(
                description=(
                    "The transport losses of natural gas pipelines are "
                    "manually set to 5e-5 per km, in line with the losses of "
                    "the other linear transport infrastructure."
                ),
            ),
        )

    def _set_capex_per_distance_transport(self) -> Attribute:
        """
        Sets the distance-specific capex of natural gas pipeline.
        """
        attr = self.capex_per_distance_transport
        return attr.set_data(
            default_value=265,
            unit="kiloEuro/GW/km",
            source=SourceInformation(
                description=(
                    "The investment cost of natural gas pipelines is based on "
                    "the TYNDP 2022 scenario building guidelines "
                    "(Tab. 14, p. 32)."
                ),
                metadata=TYNDP_SCENARIO_GUIDELINES,
            ),
        )

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of natural gas pipeline.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
