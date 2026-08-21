from __future__ import annotations

from typing import TYPE_CHECKING

from zen_europe.datasets.dataset_collections.clinker_data import ClinkerData
from zen_europe.datasets.datasets.carrier.aidres import Aidres
from zen_europe.datasets.datasets.technology.ecra_technology_papers import ECRATechnologyPapers

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator import Attribute, AssumptionInformation, ConversionTechnology
from zen_europe.utils.constants import Constants


class HydrogenToCementFuel(ConversionTechnology):
    """Class containing all data and assumptions for hydrogen-fired
    cement-kiln fuel supply (hydrogen to fuel for cement)."""

    name: str = "hydrogen_to_cement_fuel"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of hydrogen to cement fuel to fuel for
        cement.
        """
        return Attribute(
            name="reference_carrier", default_value=["fuel_for_cement"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Sets the input carrier of hydrogen to cement fuel to hydrogen.
        """
        return Attribute(
            name="input_carrier", default_value=["hydrogen"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """
        Set the output carrier of hydrogen to cement fuel to fuel for cement.
        """
        return Attribute(
            name="output_carrier", default_value=["fuel_for_cement"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of hydrogen to cement fuel.

        Assume the same lifetime as cement kilns, since the fuel supply is tied to the
        cement kiln operation.
        """
        attr = self.lifetime
        cement_kiln = self.model.conversion_technologies["cement_kiln"]
        attr.set_data(
            default_value=cement_kiln.lifetime.default_value,
            unit=cement_kiln.lifetime.unit,
            source=AssumptionInformation(
                description=(
                    "The lifetime of coal to cement fuel is assumed to be the same "
                    "as the lifetime of cement kilns, since the fuel supply is tied to "
                    "the cement kiln operation."
                ),
            ),
        )
        return attr

    def _set_conversion_factor(self) -> Attribute:
        """
        Return the conversion factor of hydrogen to cement fuel.

        """
        aidres_dataset = Aidres(source_path=self.source_path)
        return aidres_dataset.get_conversion_factor_cement_fuel(self)

    def _set_capex_specific_conversion(self) -> Attribute:
        """
        Sets the specific capital expenditure (capex) for hydrogen to
        cement fuel.

        Returns:
            Attribute: An Attribute object containing the specific capex data.
        """
        ecra_dataset = ECRATechnologyPapers(source_path=self.source_path)
        return ecra_dataset.get_capex_specific_retrofitting(self)

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing capacity of waste to cement fuel.

        Returns:
            Attribute: An Attribute object containing the existing capacity data.
        """
        clinker_demand_dataset = ClinkerData(source_path=self.source_path)
        return clinker_demand_dataset.get_capacity_existing_cement_fuel(self)
    

