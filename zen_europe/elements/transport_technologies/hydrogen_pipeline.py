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

# Lifetime and transport losses of hydrogen pipelines are taken from the energy
# transport catalogue of the Danish Energy Agency.
DEA_ENERGY_TRANSPORT = MetaData(
    name="dea_energy_transport",
    title="Technology Data for Energy Transport",
    author=["Danish Energy Agency"],
    publication="Danish Energy Agency",
    publication_year=2026,
    url=(
        "https://ens.dk/en/our-services/technology-catalogues/"
        "technology-data-energy-transport"
    ),
    note="Main distribution line, hydrogen, 70 bar.",
)

# The first hydrogen pipeline project is the Mosahyc pipeline, listed in the
# first list of Projects of Common Interest and Projects of Mutual Interest.
EC_PCI_PMI_LIST = MetaData(
    name="ec_pci_pmi_list",
    title=(
        "Technical document accompanying the first list of Projects of Common "
        "Interest and Projects of Mutual Interest"
    ),
    author=["European Commission"],
    publication="European Commission",
    publication_year=2024,
    url=(
        "https://energy.ec.europa.eu/document/download/"
        "944b96b9-4efd-44a3-bbfe-45b752b0b55f_en"
    ),
)


class HydrogenPipeline(TransportTechnology):
    """Class containing all data and assumptions for hydrogen pipeline
    transport technology."""

    name: str = "hydrogen_pipeline"

    # transport capacity of the Mosahyc hydrogen pipeline, in GWh per day
    MOSAHYC_CAPACITY = 5.5

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of hydrogen pipeline to hydrogen.
        """
        return Attribute(
            name="reference_carrier", default_value=["hydrogen"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of hydrogen pipeline.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=50,
            source=SourceInformation(
                description=(
                    "The lifetime of hydrogen pipelines is based on the main "
                    "distribution line (70 bar) of the energy transport "
                    "catalogue of the Danish Energy Agency."
                ),
                metadata=DEA_ENERGY_TRANSPORT,
            ),
        )

    def _set_construction_time(self) -> Attribute:
        """
        Sets the construction time of hydrogen pipeline.
        """
        if not self.settings.investment.use_construction_times:
            return self.construction_time
        attr = self.construction_time
        return attr.set_data(
            default_value=1,
            source=AssumptionInformation(
                description=(
                    "The construction time of hydrogen pipelines is manually "
                    "set to one year."
                ),
            ),
        )

    def _set_transport_loss_factor_linear(self) -> Attribute:
        """
        Sets the linear transport loss factor of hydrogen pipeline.
        """
        attr = self.transport_loss_factor_linear
        return attr.set_data(
            default_value=0.029 / 1000,
            unit="1/km",
            source=SourceInformation(
                description=(
                    "The transport losses of hydrogen pipelines are 2.9% per "
                    "1000 km, based on the main distribution line (70 bar) of "
                    "the energy transport catalogue of the Danish Energy "
                    "Agency."
                ),
                metadata=DEA_ENERGY_TRANSPORT,
            ),
        )

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of hydrogen pipeline.

        Capacity additions up to the size of a single reference project are
        exempt from the diffusion limit, so that a first pipeline can be built
        from a zero installed base.
        """
        attr = self.capacity_addition_unbounded
        return attr.set_data(
            default_value=self.MOSAHYC_CAPACITY / Constants.HOURS_PER_DAY,
            unit="GW",
            source=SourceInformation(
                description=(
                    "The unbounded capacity addition is the size of the "
                    f"Mosahyc hydrogen pipeline ({self.MOSAHYC_CAPACITY} GWh "
                    "per day)."
                ),
                metadata=EC_PCI_PMI_LIST,
            ),
        )

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of hydrogen pipeline.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
