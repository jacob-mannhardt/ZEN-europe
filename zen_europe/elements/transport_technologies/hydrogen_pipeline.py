from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.datasets.technology.dea_energy_transport import (
    DEAEnergyTransport,
)
from zen_europe.datasets.datasets.technology.ec_pci_pmi_list import (
    ECProjectsOfCommonInterest,
)
from zen_europe.datasets.datasets.technology.technology_diffusion_mannhardt import (
    TechnologyDiffusionMannhardt,
)

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation
from zen_creator.elements import TransportTechnology
from zen_creator.utils.attribute import Attribute


class HydrogenPipeline(TransportTechnology):
    """Class containing all data and assumptions for hydrogen pipeline
    transport technology."""

    name: str = "hydrogen_pipeline"

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
        energy_transport = DEAEnergyTransport(source_path=self.source_path)
        return energy_transport.get_lifetime(self)

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
        energy_transport = DEAEnergyTransport(source_path=self.source_path)
        return energy_transport.get_transport_loss_factor_linear(self)

    def _set_capacity_addition_unbounded(self) -> Attribute:
        """
        Sets the unbounded capacity addition of hydrogen pipeline.

        Capacity additions up to the size of a single reference project are
        exempt from the diffusion limit, so that a first pipeline can be built
        from a zero installed base.
        """
        pci_pmi_list = ECProjectsOfCommonInterest(source_path=self.source_path)
        return pci_pmi_list.get_capacity_addition_unbounded(self)

    def _set_max_diffusion_rate(self) -> Attribute:
        """
        Sets the maximum diffusion rate of hydrogen pipeline.
        """
        if not self.settings.investment.use_diffusion_rates:
            return self.max_diffusion_rate
        diffusion_rates = TechnologyDiffusionMannhardt(source_path=self.source_path)
        return diffusion_rates.get_max_diffusion_rate(self)
