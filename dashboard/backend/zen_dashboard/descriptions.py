"""Short explanations of the ZEN-europe settings, shown next to each setting.

ZEN-europe's settings classes do not describe their fields yet. The texts
below are written from how ZEN-europe uses each setting. A field that
declares a pydantic ``description`` in ZEN-europe takes precedence over the
text here, so these can move into ZEN-europe field by field.
"""

CATEGORIES: dict[str, str] = {
    "time": "Time horizon of the optimization and the year of the hourly data.",
    "region": "The countries (NUTS0 regions) that are modeled.",
    "structure": (
        "Which energy system, sectors, technologies and carriers the dataset "
        "contains. Removals are applied after all additions."
    ),
    "investment": (
        "Existing capacities, investment limits, technology diffusion and "
        "carbon capture and storage expansion."
    ),
    "emissions": "Carbon budget, annual emission limits and the EU ETS cap.",
    "cost": "Price year, learning curves and the cost assumptions of fuels and DAC.",
    "availability": "Import caps of fuels and whether demand can be shed.",
    "data_source": "Choices between alternative data sources.",
    "max_load": "Seasonal and nodal availability of nuclear power plants.",
    "scenario": (
        "Predefined sensitivities that are added to the dataset as ZEN-garden "
        "scenarios."
    ),
    "cache": (
        "Downloaded sources are cached in the raw data folder. Switch a flag on "
        "to download that source again in this run. Models with an active flag "
        "are generated one at a time."
    ),
}

FIELDS: dict[str, str] = {
    # time
    "time.reference_year": "First year of the optimization horizon.",
    "time.last_year": "Last year of the optimization horizon.",
    "time.interval_between_years": (
        "Years between two optimized years. The horizon should be a multiple of "
        "it, otherwise the last optimized year is earlier than last_year."
    ),
    "time.year_time_series": (
        "Weather and demand year of the hourly time series (demand profiles, "
        "renewable capacity factors, heat demand)."
    ),
    # region
    "region.set_nodes": "Countries that are modeled, as NUTS0 codes.",
    # structure
    "structure.energy_system": (
        "The energy system class that sets nodes, edges and system-wide parameters."
    ),
    "structure.set_sectors": (
        "Sectors that are part of the dataset. Each sector adds its "
        "technologies and carriers. Some sectors require others, e.g. "
        "district_heating requires heat."
    ),
    "structure.set_conversion_technologies": (
        "Conversion technologies added in addition to those of the sectors."
    ),
    "structure.set_storage_technologies": (
        "Storage technologies added in addition to those of the sectors."
    ),
    "structure.set_transport_technologies": (
        "Transport technologies added in addition to those of the sectors."
    ),
    "structure.set_retrofitting_technologies": (
        "Retrofitting technologies added in addition to those of the sectors."
    ),
    "structure.set_carriers": "Carriers added in addition to those of the sectors.",
    "structure.remove_sectors": (
        "Sectors to remove. Removes exactly the elements the sector declares."
    ),
    "structure.remove_technologies": (
        "Technologies or carriers to remove. A removed carrier requires that all "
        "technologies using it are removed as well."
    ),
    # investment
    "investment.allow_investment": (
        "Whether new capacity can be built at all (ZEN-garden's allow_investment)."
    ),
    "investment.use_existing_capacities": (
        "Use existing capacities of power plants, vehicles, industry, networks, "
        "etc. If off, the system is built from scratch (greenfield)."
    ),
    "investment.keep_existing_hydro_capacities": (
        "Keep the existing hydro capacities even if use_existing_capacities is off."
    ),
    "investment.use_existing_oil_to_x_capacities": (
        "Give the refinery conversions (oil to diesel, gasoline, kerosene, "
        "naphtha) existing capacities that supply today's fuel use."
    ),
    "investment.use_construction_times": (
        "Use technology construction times. If off, new capacity is available "
        "immediately."
    ),
    "investment.use_nuclear_phase_out": (
        "Limit nuclear capacity to zero in countries with a phase-out. Takes "
        "precedence over cap_nuclear_capacity_to_past_investments."
    ),
    "investment.cap_nuclear_capacity_to_past_investments": (
        "Limit nuclear capacity per country to the capacity that was ever "
        "built there."
    ),
    "investment.use_power_line_capacity_limit": (
        "Limit power line capacity per edge to what network studies foresee "
        "(see data_source.potential_capacity_power_line). If off, unlimited."
    ),
    "investment.allow_offshore_chemical_pipelines": (
        "Allow hydrogen, ammonia, methanol and olefin pipelines on edges that "
        "cross the sea."
    ),
    "investment.account_for_offshore_transport": (
        "Use the higher offshore cost of transport technologies on edges "
        "between non-adjacent countries."
    ),
    "investment.use_battery_e2p_ratio": (
        "Constrain the battery energy-to-power ratio to the NREL range."
    ),
    "investment.use_200y_lifetime_hydro": (
        "Give hydro plants a lifetime of 200 years so existing plants never retire."
    ),
    "investment.use_diffusion_rates": (
        "Limit how fast technologies can grow (maximum diffusion rate, "
        "Mannhardt et al. 2024). If off, capacity can grow without limit."
    ),
    "investment.use_inf_spillover_rate": (
        "Let technology knowledge spill over between countries without limit, "
        "so diffusion is limited at the European level."
    ),
    "investment.use_unbounded_market_share": (
        "Exempt a small market share (2%) from the diffusion limit, so new "
        "technologies can start from zero."
    ),
    "investment.use_unbounded_capacity_addition_carbon": (
        "Exempt one reference project of carbon capture technologies from the "
        "diffusion limit, so a first plant can be built."
    ),
    "investment.knowledge_depreciation_rate": (
        "Annual depreciation of technology knowledge for the diffusion limit. "
        "Only 0.1 and 0.2 are available."
    ),
    "investment.set_future_CCS_investments": (
        "Include announced future DAC and carbon storage projects as existing "
        "capacity, not only those built before the reference year."
    ),
    "investment.consider_carbon_storage_expansion": (
        "Include planned carbon storage expansions and projects that are not in "
        "operation or at final investment decision."
    ),
    # emissions
    "emissions.use_carbon_budget": (
        "Limit cumulative emissions over the horizon by Europe's share of the "
        "global carbon budget."
    ),
    "emissions.use_carbon_annual_limit": "Limit emissions in every year.",
    "emissions.use_annual_limit_overshoot": (
        "Allow the annual limit to be exceeded at a penalty price instead of "
        "making it a hard limit."
    ),
    "emissions.use_EU_ETS_cap": "Use the EU ETS cap as the annual emission limit.",
    "emissions.temperature_increase": (
        "Temperature target of the IPCC AR6 carbon budget, in °C. One of 1.5, "
        "1.7, 2."
    ),
    "emissions.probability_carbon_budget": (
        "Probability of reaching the temperature target. One of 0.17, 0.33, "
        "0.5, 0.67, 0.83."
    ),
    # cost
    "cost.price_year": (
        "Year whose money all costs are expressed in (inflation-adjusted with "
        "ECB HICP)."
    ),
    "cost.use_learning_curves": (
        "Let technology costs fall over time. If off, today's cost is used in "
        "all years."
    ),
    "cost.use_nodal_biomass_prices": (
        "Use country-specific biomass prices instead of one European price."
    ),
    "cost.assume_oil_price_for_diesel_and_gasoline": (
        "Price diesel and gasoline like crude oil, i.e. without the refining "
        "price spread."
    ),
    "cost.dac_cost_source": (
        "Source of DAC costs: 'sievert' uses the experience curves of Sievert et "
        "al. (2024), 'tech_db' uses the technology cost database (DEA)."
    ),
    "cost.dac_technology": "DAC technology whose Sievert et al. (2024) cost is used.",
    "cost.dac_deployment_pathway": (
        "Global DAC deployment pathway along which the Sievert et al. (2024) "
        "experience curve is evaluated."
    ),
    # availability
    "availability.cap_waste_import": (
        "Cap waste availability by the national supply reported by Eurostat. "
        "If off, unlimited."
    ),
    "availability.cap_coal_import": (
        "Cap hard coal and lignite availability by the national supply reported "
        "by Eurostat. If off, unlimited."
    ),
    "availability.cap_oil_import": (
        "Cap crude oil availability by the national supply reported by "
        "Eurostat. If off, unlimited."
    ),
    "availability.annual_cap_biomass_import": (
        "Limit biomass by an annual ENSPRESO potential instead of a limit per hour."
    ),
    "availability.allow_heat_demand_shedding": (
        "Allow heat demand to be unmet at a high penalty price."
    ),
    "availability.allow_all_demand_shedding": (
        "Allow every demand to be unmet at a high penalty price."
    ),
    # data_source
    "data_source.use_full_scigrid_dataset": (
        "Take existing gas pipelines from the full SciGRID_gas dataset instead "
        "of the ENTSOG capacity map."
    ),
    "data_source.use_OG_carbon_storage_limit": (
        "Limit carbon storage by the oil and gas extraction of each country."
    ),
    "data_source.use_monthly_entsoe_ntc": (
        "Use monthly instead of annual ENTSO-E net transfer capacities."
    ),
    "data_source.potential_capacity_power_line": (
        "Power line capacity limit: 'candidates' (existing + all investment "
        "candidates of the system needs study), 'tyndp' (TYNDP 2050 export "
        "capacity) or 'both' (the larger)."
    ),
    "data_source.use_plant_level_hydro_capacity": (
        "Take existing hydro capacities from plant-level databases instead of PECD."
    ),
    # max_load
    "max_load.use_seasonal_nuclear_max_load": (
        "Use a seasonal maximum load profile for nuclear plants."
    ),
    "max_load.use_nodal_nuclear_max_load": (
        "Use country-specific nuclear profiles. If off, one European profile."
    ),
    # scenario
    "scenario.run_default_scenario": (
        "Whether ZEN-garden also runs the dataset without scenario changes. Set "
        "to false to run only the scenarios."
    ),
    "scenario.sensitivity_demand": (
        "Add low (x0.75) and high (x1.25) demand scenarios per economic sector."
    ),
    "scenario.sensitivity_discount_rate": (
        "Add scenarios that scale the discount rate by 0, 0.5 and 1.5."
    ),
    "scenario.sensitivity_biomass": (
        "Add low and high biomass availability scenarios (ENSPRESO low and high)."
    ),
    "scenario.sensitivity_no_diffusion_rate": (
        "Add a scenario without diffusion limits for all technologies."
    ),
}


def describe_cache_field(field: str) -> str:
    """The explanation of an overwrite flag of the cache category."""
    source = field.removeprefix("overwrite_")
    return f"Download or rebuild the cached {source} data again in this run."
