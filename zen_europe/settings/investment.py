from typing import Optional

from zen_creator.utils.settings import SettingsCategory


class InvestmentSettings(SettingsCategory):
    """Investment and capacity settings."""

    name: str = "investment"

    allow_investment: bool = True # NOTE: DONE
    use_retrofit: bool = True  # TODO remove
    use_existing_capacities: bool = True
    # keeps the existing hydro capacities even if use_existing_capacities is False
    keep_existing_hydro_capacities: bool = False
    use_battery_capacity_existing: bool = True
    use_existing_oil_to_x_capacities: bool = False
    use_construction_times: bool = True # NOTE: DONE
    use_nuclear_phase_out: bool = True # takes precedence over cap_nuclear_capacity_to_past_investments # NOTE DONE
    cap_nuclear_capacity_to_past_investments: bool = True # NOTE DONE
    use_power_line_capacity_limit: bool = True
    use_chemical_pipelines: bool = False
    account_for_offshore_transport: bool = False
    use_battery_e2p_ratio: bool = False
    storage_charge_discharge_binary: Optional[bool] = None
    use_200y_lifetime_hydro: bool = True
    use_diffusion_rates: bool = True
    use_inf_spillover_rate: bool = True
    use_unbounded_market_share: bool = True
    use_unbounded_capacity_addition_carbon: bool = True
    knowledge_depreciation_rate: float = 0.1
    set_future_CCS_investments: bool = False
