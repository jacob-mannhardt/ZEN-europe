from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)
from zen_europe.utils.constants import Constants

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation, MetaData
from zen_creator.elements import TransportTechnology
from zen_creator.utils.attribute import Attribute, SourceInformation

# The lifetime of CO2 pipelines is taken from the carbon capture, transport and
# storage catalogue of the Danish Energy Agency.
DEA_CCS = MetaData(
    name="dea_ccs",
    title="Technology Data for Carbon Capture, Transport and Storage",
    author=["Danish Energy Agency"],
    publication="Danish Energy Agency",
    publication_year=2026,
    url=(
        "https://ens.dk/en/analyses-and-statistics/"
        "technology-data-carbon-capture-transport-and-storage"
    ),
)


class CarbonPipeline(TransportTechnology):
    """Class containing all data and assumptions for carbon (CO2) pipeline
    transport technology."""

    name: str = "carbon_pipeline"

    def __init__(self, model: Model, power_unit: str = "tCO2/h"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of carbon pipeline to carbon.
        """
        return Attribute(
            name="reference_carrier", default_value=["carbon"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of carbon pipeline.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=50,
            source=SourceInformation(
                description=(
                    "The lifetime of CO2 pipelines is based on the carbon "
                    "capture, transport and storage catalogue of the Danish "
                    "Energy Agency."
                ),
                metadata=DEA_CCS,
            ),
        )

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of carbon pipeline.

        Capacity additions up to the size of a single reference project are
        exempt from the diffusion limit, so that a first pipeline can be built
        from a zero installed base.
        """
        attr = self.capacity_addition_unbounded
        if not self.settings.investment.use_unbounded_capacity_addition_carbon:
            return attr
        return attr.set_data(
            default_value=Constants.DUIVEN_CAPTURE_CAPACITY / Constants.HOURS_PER_YEAR,
            unit="tCO2/h",
            source=AssumptionInformation(
                description=(
                    "The unbounded capacity addition is the size of the Duiven "
                    "carbon capture plant (0.1 MtCO2 per year)."
                ),
            ),
        )

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of carbon pipeline.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
