# Implementation TODO: Technologies & Carriers

Checklist of every technology/carrier from `data/config.yaml` that needs a concrete
`zen_creator` element class in `zen_europe/elements/`, plus the raw-data `Dataset`
classes each one depends on. For every framework attribute, the detail sections below
indicate whether the legacy `Input_data_creation` pipeline populates it with real data
(and from which source) or leaves it at the generic framework default.

Legend used throughout: **REAL** = real data source (built or to be built as a `Dataset`).
**manual: X** = explicit hardcoded scalar/assumption (not a `Dataset`, just a literal
value with a citation — same pattern as `PumpedHydro._set_lifetime`). **default** =
legacy never sets it either; leave at the `zen_creator` framework default. Flag tags
`[XYZ]` refer to legacy scenario config flags — see the footnote glossary in each
section; they mark branches whose applicability depends on which scenario is being
reproduced and should be resolved with the domain owner before hardcoding a choice.

---

## Checklist

### Already touched in `zen_europe` (partial — see §5 for exact gaps)
- [~] `energy_system_nuts0` — nodes/edges real (NUTSshp/TYNDP), carbon budget/discount rate/spillover/WACC not yet ported
- [~] `electricity` (carrier) — **stub only**, `_set_demand` is a no-op pass-through; no real data ported at all
- [x] `biomass` (carrier) — `availability_import` real (ENSPRESO); `price_import` stub (empty method); several sub-branches (annual-cap, sensitivity) not ported
- [~] `photovoltaics` (conversion tech) — `_set_input/_set_output/_set_lifetime/_set_conversion_factor` are pass-through templates; no real data ported
- [~] `pumped_hydro` (storage tech) — `reference_carrier` real; `lifetime` wrong placeholder (25, legacy=55); everything else default
- [~] `power_line` (transport tech) — `reference_carrier` real; `lifetime` not even set (NaN); everything else default

### Carriers (31)
- [ ] ammonia
- [x] biomass — see gap note above
- [ ] biomethane
- [ ] carbon
- [ ] clinker
- [ ] crude_oil
- [ ] diesel
- [ ] district_heat
- [ ] electricity — see gap note above
- [ ] fuel_for_cement
- [ ] gasoline
- [ ] hard_coal
- [ ] heat
- [ ] hydrogen
- [ ] kerosene
- [ ] lignite
- [ ] lng
- [ ] methanol
- [ ] naphtha
- [ ] natural_gas
- [ ] natural_gas_industry
- [ ] oil
- [ ] olefin
- [ ] passenger_mileage
- [ ] primary_steel
- [ ] secondary_steel
- [ ] shipping
- [ ] truck_mileage
- [ ] uranium
- [ ] waste
- [ ] wet_biomass

### Conversion technologies (70)
- [ ] BEV, BF_BOF, DAC, EAF, H2_DRI, HDT_BET, HDT_FCEV, HDT_diesel, ICE_diesel, ICE_petrol, NG_DRI, SMR
- [ ] ammonia_ICE_ship, anaerobic_digestion, biomass_boiler, biomass_boiler_DH, biomass_plant, biomass_to_cement_fuel, biomethane_conversion, carbon_storage, cement_kiln, coal_to_cement_fuel, diesel_ICE_ship, district_heating_grid, electrode_boiler, electrode_boiler_DH, electrolysis, fischer_tropsch, fuel_cell, gasification, haber_bosch, hard_coal_boiler_DH, hard_coal_plant, heat_pump, heat_pump_DH, hydrogen_FC_ship, hydrogen_to_cement_fuel, industrial_gas_consumer, lignite_coal_plant, lng_terminal, methanation, methanol_ICE_ship, methanol_from_biomass, methanol_from_hydrogen, methanol_from_natural_gas, natural_gas_boiler, natural_gas_boiler_DH, natural_gas_turbine, nuclear, oil_boiler, oil_boiler_DH, oil_plant, oil_to_diesel_conversion, oil_to_gasoline_conversion, oil_to_kerosene_conversion, oil_to_naphtha_conversion, olefin_from_methanol, olefin_from_naphtha, pyrolysis, refining, reservoir_hydro, run-of-river_hydro, waste_boiler_DH, waste_plant, waste_to_cement_fuel, wind_offshore, wind_onshore
- [x] photovoltaics — see gap note above

### Retrofitting technologies (6)
- [ ] natural_gas_turbine_CCS, biomass_plant_CCS, SMR_CCS, cement_post_comb, BF_BOF_CCS, NG_DRI_CCS

### Storage technologies (5)
- [ ] battery
- [x] pumped_hydro — see gap note above
- [ ] natural_gas_storage
- [ ] oil_storage
- [ ] salt_cavern_storage

### Transport technologies (5)
- [x] power_line — see gap note above
- [ ] natural_gas_pipeline
- [ ] carbon_pipeline
- [ ] hydrogen_pipeline
- [ ] oil_pipeline

### New `Dataset`/`TechnoEconomicDataset` classes implied by the tables below (not yet built, beyond `Enspreso`)
- [ ] `Eurostat` — efficiencies, electricity generation, heat balances, industrial gas, vehicle stats
- [ ] `Entsoe` — generation, existing capacity, transmission capacity, demand, nuclear capacity factor
- [ ] `OPSD` — power-plant existing capacity
- [ ] `IRENA` — renewable existing capacity
- [ ] `BNEF` — capacities (battery) + fuel/carrier prices + some conversion-tech costs
- [ ] `JRCHydro` — hydro capacity existing/limit (JRC Hydro-power Database)
- [ ] `RenewablesNinja` — PV/wind capacity factors
- [ ] `AntoniniCapacityFactor` — alternative PV/onshore-wind capacity factors
- [ ] `TroendleHydro` — reservoir/run-of-river capacity factors
- [ ] `When2Heat` — heat-pump COP, heat demand shape
- [ ] `SciGrid` — gas pipeline/LNG terminal/storage infrastructure
- [ ] `ENTSOG` — gas capacities aggregated (border points, industrial clusters)
- [ ] `Potencia`, `DIW`, `TYNDPCost`, `DEA`, `EUREF`, `LUW` — the 6 techno-economic cost agencies (capex/opex/lifetime/construction_time/efficiency)
- [ ] `CostsAdditionalTechnologies` — the curated `costs_additional_technologies.xlsx` fallback
- [ ] `VehicleTransportParams` — `vehicle_tech_parameters.csv` / `HDT_params.xlsx` (passenger + truck)
- [ ] `CarbonBudget`, `Derisking` — energy-system-level (see prior migration roadmap discussion, not re-covered here)
- [ ] `ENSPRESOBiomassPrices` extension to `Enspreso` — biomass cost sheet (currently only availability is ported)
- [ ] `IOGP`/`CATF` CCS-related capacity datasets (carbon_storage capacity_limit/existing)

---

## §1 — Carriers: full attribute sourcing

`Carrier` framework attributes: `demand`, `availability_import`, `availability_export`,
`availability_import_yearly`, `availability_export_yearly`, `price_import`, `price_export`,
`carbon_intensity_carrier_import`, `carbon_intensity_carrier_export`, `price_shed_demand`.

Table assumes the "long-term/standard" scenario (`short_term_analysis=False`); flagged
cells (`[XYZ]`) switch behavior under alternate scenario flags — see glossary below.

| Carrier | demand | availability_import | availability_export | avail._import_yearly | avail._export_yearly | price_import | price_export | carbon_int._import | carbon_int._export | price_shed_demand |
|---|---|---|---|---|---|---|---|---|---|---|
| ammonia | REAL: AIDRES/IFA `create_ammonia_demand` + yearly-var | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| biomass | default | REAL: ENSPRESO `_create_availability_biomass` (ENS_Med) [BIO] | default | REAL [BIO-annual/ST] else default | default | REAL: ENTSOE/TYNDP `carrier_prices.csv`×MWh2GJ + yearly-var | default | manual: 0 (special-cased, biogenic) + upstream 0.00252 if enabled | default | default(∞) [SHED] |
| biomethane | default | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| carbon | default | manual: 0 (unit only) | manual: 0 (unit only) | default | default | default | default | default | default | default(∞) [SHED] |
| clinker | REAL: AIDRES `create_clinker_demand` | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| crude_oil | default | default | default | default | default | REAL: BNEF "oil" row (unconditional) + yearly-var | default | REAL: 0.26388 t/MWh (+upstream 0.03852 if enabled) | default | default(∞) [SHED] |
| diesel | default | manual: 0 [REF] else default | default | default | default | REAL: BNEF diesel row (or =oil price [flag]) + yearly-var; [ST]→default | default | REAL: 0.26676 t/MWh | default | default(∞) [SHED] |
| district_heat | default | manual: 0 | manual: 0 | default | default | default | default | default | default | manual: ∞ |
| **electricity** | **STUB — no-op, returns default 0** | manual: 0 (legacy; not ported) | manual: 0 (legacy; not ported) | default | default | default | default | manual: 0 (legacy; not ported) | manual: 0 (legacy; not ported) | manual: 4000/1e4 [flag] (legacy; not ported) |
| fuel_for_cement | default | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| gasoline | default | manual: 0 [REF] else default | default | default | default | REAL: BNEF gasoline row (or =oil price [flag]) + yearly-var; [ST]→default | default | REAL: 0.24948 t/MWh | default | default(∞) [SHED] |
| hard_coal | default | REAL: `_create_availability_coal` [CAP] else default/manual 0 | manual: ∞ | REAL [CAP] or manual 0; else default | default | REAL: BNEF (or TYNDP `carrier_prices_for21.csv` [ST]) + yearly-var | manual: 0 | REAL: 0.34060 t/MWh (+upstream 0.0576 if enabled) | manual credit [COAL2] else default 0 | default(∞) [SHED] |
| heat | REAL: when2heat×EU-buildings `create_heat_demand` + optional low-yearly-var [flag] | manual: 0 | manual: 0 | default | default | default | default | default | default | manual: 4000/1e4 [flag] or ∞ |
| hydrogen | conditional REAL: legacy H2-study copy, only if `use_industrial_sector=False` [IND]; else default | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| kerosene | REAL: Eurostat aviation branch | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| lignite | default | REAL: `_create_availability_coal` [CAP] else default/manual 0 | default | REAL [CAP] else default | default | REAL: ENTSOE/TYNDP (unconditional, not in bnef index) + yearly-var | default | REAL: 0.36354 t/MWh (+upstream 0.00612) | default | default(∞) [SHED] |
| lng | default | REAL: `_create_availability_lng` (ENTSOG regions × terminal capacity) | default | REAL only [ST]; else default | default | REAL: BNEF "lng"×lng_price_excess; [ST]→gas_avg×lng_price_excess + yearly-var | default | REAL: 0.20196 t/MWh (+upstream 0.05575) | default | default(∞) [SHED] |
| methanol | REAL: AIDRES `create_methanol_demand` (scaled to EU total) | manual: 0 | manual: 0 | default | default | default | default | default | default | default(∞) [SHED] |
| naphtha | default (feeds olefin demand internally) | manual: 0 | manual: 0 | default | default | default | default | default | default | default(∞) [SHED] |
| natural_gas | default | REAL: `_create_availability_gas` (SciGrid+manual+ENTSOG+Norway+production) | manual: 0 | default (never written) | default | REAL: BNEF; [ST]→gas_price_average (Eurostat EU avg) + yearly-var | default | REAL: 0.20196 t/MWh (+upstream 0.05324) | default | default(∞) [SHED] |
| natural_gas_industry | conditional REAL: Eurostat industrial-gas balance [IND]; else default | manual: 0 | manual: 0 | default | default | default | default | default | default | manual: ∞ or 1e4 [SHED] |
| oil | default | manual: 0 (crude_oil modeled); REAL via `_create_availability_oil` [CAP] may write nothing | default | REAL [CAP] else manual 0/default | default | REAL: BNEF "oil"; [ST]→TYNDP `carrier_prices_for21.csv` + yearly-var | default | REAL: 0.26676 t/MWh (+upstream 0.03852) | default | default(∞) [SHED] |
| olefin | REAL: naphtha→olefin conversion branch | manual: 0 | manual: 0 | default | default | default | default | default | default | default(∞) [SHED] |
| passenger_mileage | REAL: `slp_passenger` travel-demand series | manual: 0 | manual: 0 | default | default | default | default | default | default | manual: 10000 €/unit |
| primary_steel | REAL: AIDRES `create_steel_demand` (primary share) + yearly-var | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| secondary_steel | REAL: AIDRES `create_steel_demand` (secondary share) + yearly-var | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| shipping | REAL: Eurostat maritime ÷ diesel_ICE_ship conv. factor | manual: 0 | default | default | default | default | default | default | default | default(∞) [SHED] |
| truck_mileage | REAL: `slp_truck` travel-demand series | manual: 0 | manual: 0 | default | default | default | default | default | default | default(∞) [SHED] |
| uranium | default | default | default | default | default | REAL: ENTSOE/TYNDP (unconditional, not in bnef index) + yearly-var | default | REAL: 0 t/MWh fuel (+upstream 0.00504) | default | default(∞) [SHED] |
| waste | default | default (only real if `_create_availability_waste` flags active [CAP]) | manual: 0 | REAL [ST or annual_cap]; else default | default | manual: 0 (hardcoded, always) — no yearly-var | default | REAL: 0.33012 t/MWh (upstream=0) | default | default(∞) [SHED] |
| wet_biomass | default | manual 0 fallback; REAL via `_create_availability_biomass` (MINBIOGAS1/MINBIOSLU1) [BIO] | default | REAL [BIO-annual/ST]; else default | default | REAL: mean of `ENSPRESO_biomass_prices` cost sheet + yearly-var (nodal if flag) | default | default — not in `carbon_intensity_carrier_total` | default | default(∞) [SHED] |

**Flag glossary**: `[SHED]` = generic catch-all — if `allow_all_demand_shedding` and `price_shed_demand` still ∞, reset to 1e4. `[ST]` = `short_term_analysis` alternate branch. `[CAP]` = coal/oil/waste availability only written if `cap_coal_oil_import`/`cap_waste_import`/`annual_cap_coal_oil_import` set — otherwise **nothing written at all**. `[REF]` = `use_refining_sector`. `[IND]` = `use_industrial_gas_demand` / `use_industrial_sector`. `[BIO]` = biomass branch depends on `short_term_analysis`/`annual_cap_biomass_import`/`use_biomass_projections` — table shows the ENSPRESO (`use_biomass_projections=True`) branch, matching what `biomass.py` currently ports. `[COAL2]` = `allow_hard_coal_export_emission_credit`.

**Notes**:
- POTEnCIA carrier-price fallback (`get_carrier_identifier`) is effectively dead code — every carrier it would match is already caught by an earlier BNEF/ENTSOE branch.
- `oil` and `crude_oil` are priced from the same BNEF "oil" series via two independent code paths — worth keeping as two independent `Dataset` calls even though the number coincides today.
- 31 carrier names total (config.yaml lists 31, not 30 as originally estimated).

---

## §2 — Conversion technologies: identity attributes (reference/input/output carrier, conversion_factor, lifetime, construction_time)

`reference_carrier`/`input_carrier`/`output_carrier` are **always REAL** — read directly
from `NUTS0_Source_Data/03-conversion_technologies/set_conversion_technologies.json` for
every one of the 70+6 technologies. Trivial 1:1 port, not tabulated per-row below.

### Electricity generation
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| photovoltaics | N/A (no input carrier) | REAL: cost DB median | REAL: JRC POTEnCIA, may be overwritten by cost DB |
| wind_onshore | N/A | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| wind_offshore | N/A | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| run-of-river_hydro | N/A | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| reservoir_hydro | N/A | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| hard_coal_plant | REAL: Eurostat efficiency | REAL: cost DB, **manual override → 46** | REAL: JRC POTEnCIA / cost DB |
| lignite_coal_plant | REAL: Eurostat efficiency | REAL: cost DB, **manual override → 46** | REAL: JRC POTEnCIA / cost DB |
| natural_gas_turbine | REAL: Eurostat efficiency | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| nuclear | REAL: Eurostat efficiency | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| oil_plant | REAL: Eurostat efficiency | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| biomass_plant | REAL: Eurostat efficiency | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| waste_plant | REAL: Eurostat efficiency | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |

### Heat / district-heat
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| natural_gas_boiler | REAL: cost DB (DEA_ih), fallback manual 0.93 | REAL if DB cost data available; else default | default (DEA_ih doesn't extract this) |
| heat_pump | REAL: cost DB (DEA_ih), fallback manual 3.7 | REAL if available; else default | default |
| oil_boiler | REAL: cost DB (DEA_ih), fallback manual 0.93 | REAL if available; else default | default |
| biomass_boiler | REAL: cost DB (DEA_ih), fallback manual 0.85 | REAL if available; else default | default |
| electrode_boiler | REAL: cost DB (DEA_ih), fallback manual 1/1.01 | REAL if available; else default | default |
| natural_gas_boiler_DH | REAL: cost DB (DEA main+EUREF), no fallback | REAL if available | REAL: cost DB (DEA main); else default |
| heat_pump_DH | REAL: cost DB (DEA/EUREF), no fallback | REAL if available | REAL: cost DB (DEA); else default |
| oil_boiler_DH | REAL: cost DB (DEA/EUREF), fallback manual 0.93 | REAL if available | REAL: cost DB (DEA); else default |
| waste_boiler_DH | REAL: cost DB (DEA/EUREF), no fallback | REAL if available | REAL: cost DB (DEA); else default |
| biomass_boiler_DH | REAL: cost DB (DEA/EUREF), no fallback | REAL if available | REAL: cost DB (DEA); else default |
| hard_coal_boiler_DH | REAL: cost DB (EUREF only), fallback manual 0.93 | REAL if available | **default** — EUREF doesn't extract construction_time, not in DEA main list |
| electrode_boiler_DH | REAL: cost DB (DEA/EUREF), no fallback | REAL if available | REAL: cost DB (DEA); else default |
| district_heating_grid | **manual: 0.86** (1−0.14, not covered by any catalog) | **manual: 40** (DEA table 13) | **manual: 1** |

### Gas infrastructure / carbon
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| lng_terminal | **manual: 1** | **manual: 30** (Brauers et al. 2021) | **manual: 4** |
| industrial_gas_consumer | **manual: 1** | **manual: 100** | default |
| carbon_storage | N/A (input=output=carbon, no dependent carrier) | **manual: 40** (GCCSI report) | **manual: 6** |

### Hydrogen / PtX
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| SMR | **manual dict**: `{natural_gas:1.2987, electricity:0.0413}` (H2 supply-chain source) | REAL: cost DB (LUW "Steam Methane Reforming") | default (LUW doesn't extract this) |
| electrolysis | **manual dict** (DEA renewable-fuels PEMEC) | REAL: cost DB (DEA_rf+LUW) | REAL: cost DB (DEA_rf) |
| gasification | **manual dict** (DEA bio-SNG) | REAL: cost DB (DEA_rf) | REAL: cost DB (DEA_rf) |
| fischer_tropsch | **manual dict** (DEA H2-to-Jet-Fuel) | REAL: cost DB (DEA_rf+LUW) | REAL: cost DB (DEA_rf) |
| methanation | **manual dict** (Götz 2016) | REAL: cost DB (DEA_rf+LUW) | REAL: cost DB (DEA_rf) |
| anaerobic_digestion | **manual dict** (DEA biogas plant) | REAL: cost DB (DEA_rf) | REAL: cost DB (DEA_rf) |
| biomethane_conversion | **manual dict** (DEA amine scrubber) | REAL: cost DB (DEA_rf) | REAL: cost DB (DEA_rf) |
| fuel_cell | REAL: cost DB efficiency (Potencia+DEA) | REAL: cost DB | REAL: cost DB (DEA main); else default |
| DAC | **manual dict**: `{electricity:0.8, heat:9.5/3.6}` (DEA CCS PDF) | REAL: cost DB (DEA_ccs) | REAL: cost DB (DEA_ccs) |
| refining | **manual (explicit branch)**: `{crude_oil:1, hydrogen:0.541×MWh2toe}` | **manual: 30** | **manual: 3** |

### Methanol / olefins
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| methanol_from_natural_gas | **manual dict** (sciencedirect source) | **manual: 25** | **manual: 3** |
| methanol_from_biomass | **manual dict** (DEA "Bio Methanol") | REAL: cost DB (DEA_rf) | REAL: cost DB (DEA_rf) |
| methanol_from_hydrogen | **manual dict** (DEA "Methanol from H2+CO2") | REAL: cost DB (DEA_rf) | REAL: cost DB (DEA_rf) |
| olefin_from_methanol | **manual dict** (AIDRES p.71) | **manual: 25** | **manual: 3** |
| olefin_from_naphtha | **manual dict** (AIDRES p.71) | **manual: 25** | **manual: 3** |

### Ammonia / Cement
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| haber_bosch | **manual dict** (DEA "Green Ammonia plant") | REAL: cost DB (DEA_rf) | REAL: cost DB (DEA_rf) |
| cement_kiln | **manual dict** (3.7 GJ/t, AIDRES/materialeconomics) | default (no coverage anywhere) | default |
| coal_to_cement_fuel | **manual: 1** | default | default |
| hydrogen_to_cement_fuel | **manual**: `2.46/consumption_hard_coal` | default | default |
| waste_to_cement_fuel | **manual**: `2.46/consumption_hard_coal` | default | default |
| biomass_to_cement_fuel | **manual**: `2.77/consumption_hard_coal` | default | default |

### Steel
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| BF_BOF | **manual dict** (Agora steel-transformation) | **default — explicit TODO in legacy code, not implemented there either** | default |
| H2_DRI | **manual dict** | default (same TODO) | default |
| NG_DRI | **manual dict** | default (same TODO) | default |
| EAF | **manual dict** | default (same TODO) | default |
| pyrolysis | **manual dict**, re-normalized to `oil` reference carrier | REAL: cost DB (DEA_rf) | REAL: cost DB (DEA_rf) |

### Shipping
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| diesel_ICE_ship | **manual: 1/0.45** (Korberg 2021) | **manual: 30** | default |
| hydrogen_FC_ship | **manual dict** | **manual: 15** | default |
| methanol_ICE_ship | **manual: 1/0.45** | **manual: 30** | default |
| ammonia_ICE_ship | **manual: 1/0.45** | **manual: 30** | default |

### Oil refining derivatives
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| oil_to_gasoline_conversion | **manual: 1** | **manual: 100** | default |
| oil_to_diesel_conversion | **manual: 1** | **manual: 100** | default |
| oil_to_naphtha_conversion | **manual: 1** | default (not in the manual-lifetime branch) | default |
| oil_to_kerosene_conversion | **manual: 1** | default | default |

### Road transport
| Tech | conversion_factor | lifetime | construction_time |
|---|---|---|---|
| BEV | REAL: `vehicle_param` table | **default — legacy has a `get_transport_constants("lifetime")=20` but it's dead/commented-out code** | default |
| ICE_diesel | REAL: `vehicle_param` table | default | default |
| ICE_petrol | REAL: `vehicle_param` table | default | default |
| HDT_diesel | REAL: `truck_param` table | default | default |
| HDT_BET | REAL: `truck_param` table | default | default |
| HDT_FCEV | REAL: `truck_param` table | default | default |

### Retrofitting technologies (6) — `retrofit_reference_carrier` always = `reference_carrier` (= "carbon" for all 6)
| Tech | conversion_factor / retrofit_flow_coupling_factor | lifetime | construction_time |
|---|---|---|---|
| natural_gas_turbine_CCS | REAL+manual: cost-DB efficiency delta (base tech has DB coverage) combined with manual `CCS_capture_rate=0.88` and REAL carbon-intensity | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| biomass_plant_CCS | REAL+manual: same mechanism | REAL: cost DB | REAL: JRC POTEnCIA / cost DB |
| SMR_CCS | **manual dict**: `get_conversion_factor_hydrogen("SMR_CCS")` (DEA post-combustion retrofit values) — base tech has no cost-DB efficiency so falls to explicit branch | REAL: cost DB (DEA_ccs, proxy entry) | REAL: cost DB (DEA_ccs) |
| cement_post_comb | **manual**: `clinker_carbon_intensity(0.54) × carbon_capture_rate(0.9)`, unit-scaled | REAL: cost DB (DEA_ccs, cement-kiln-retrofit proxy) | REAL: cost DB (DEA_ccs) |
| BF_BOF_CCS | **manual**: `carbon_capture_BF_BOF=1.36` tCO2eq/tsteel (Agora), unit-scaled — note: a `get_conversion_factor_steel` dict value is computed but superseded/unused (dead code) | REAL: cost DB (DEA_ccs proxy) | REAL: cost DB (DEA_ccs) |
| NG_DRI_CCS | **manual**: `carbon_capture_NG_DRI=0.35` tCO2eq/tsteel (Agora), unit-scaled — same dead-code note | REAL: cost DB (DEA_ccs proxy) | REAL: cost DB (DEA_ccs) |

**Open question to resolve before implementing the 3 DB-covered retrofit techs**
(natural_gas_turbine_CCS, biomass_plant_CCS, SMR_CCS): whether cost is an absolute
DB value or a delta-from-base-tech depends on a `take_delta_cost_from_base_tech` flag
read from a technology-attributes JSON not covered in this analysis — check that file
before finalizing capex sourcing for those three.

---

## §3 — Conversion technologies: capacity attributes (capacity_existing, capacity_limit, max_load)

`capacity_addition_min`/`capacity_addition_max`/`capacity_investment_existing`/
`max_diffusion_rate` are **never populated by any extractor** for any of the 76
technologies in the legacy pipeline — always stays at framework default (except
`max_diffusion_rate`, which is driven by a single global scenario-flag mechanism
identical across all techs, not per-tech data).

Important quirk: several dispatches are `if/elif` chains gated by scenario flags —
if an earlier name-matching branch's flag is off, the tech does **not** fall through
to a later, more specific branch. Flagged `[flag]` below.

| Technology | capacity_existing | capacity_limit | max_load |
|---|---|---|---|
| BEV | REAL: Eurostat vehicle-stock × mileage | default (inf) | REAL: `slp_passenger` profile |
| BF_BOF | REAL: `cd.steel_demand` × primary-steel share | default (inf) | default (1.0) |
| DAC | REAL: "DAC Announced Deployments" xlsx | default (inf) | default (1.0) |
| EAF | REAL: `cd.steel_demand` × secondary-steel share | default (inf) | default (1.0) |
| H2_DRI | default (0) | default (inf) | default (1.0) |
| HDT_BET | REAL: truck-fleet/mileage data | default (inf) | REAL: `slp_truck` profile |
| HDT_FCEV | REAL: truck-fleet/mileage data | default (inf) | REAL: `slp_truck` profile |
| HDT_diesel | REAL: truck-fleet/mileage data | default (inf) | REAL: `slp_truck` profile |
| ICE_diesel | REAL: Eurostat vehicle-stock | manual 0 from `phase_out_year` [flag `force_ice_phase_out`]; else default (inf) | REAL: `slp_passenger` profile |
| ICE_petrol | REAL: Eurostat vehicle-stock | same ICE phase-out logic [flag] | REAL: `slp_passenger` profile |
| NG_DRI | default (0) | default (inf) | default (1.0) |
| SMR | REAL: H2 Observatory refinery + ammonia-plant xlsx | default (inf) | default (1.0) |
| ammonia_ICE_ship | default (0) | default (inf) | manual: 0.75×5280/8760≈0.452 |
| anaerobic_digestion | default (0) | default (inf) | default (1.0) |
| biomass_boiler | REAL: Eurostat/JRC-IDEES heating-share × when2heat heat_demand | default (inf) | REAL: `_max_load_heat` (when2heat shape) |
| biomass_boiler_DH | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_district_heat` (when2heat + DH-share xlsx) |
| biomass_plant | REAL: ENTSO-E+OPSD+IRENA (or BNEF [flag]) | default (inf) | default = JRC POTEnCIA technical availability (has `nameJRC`) |
| biomass_to_cement_fuel | REAL: `cd.clinker_demand` × fuel_consumption_kiln × fuel-share | default (inf) | default (1.0) |
| biomethane_conversion | REAL: European Biogas Association `biomethane_production.xlsx` | default (inf) | default (1.0) |
| carbon_storage | REAL: IOGP CO2-storage-projects xlsx | REAL: IOGP (default) or CATF xlsx or O&G-extraction-derived [flags] | default (1.0) |
| cement_kiln | default (0) | default (inf) | default (1.0) |
| coal_to_cement_fuel | REAL: `_existing_capacity_cement_fuel` | default (inf) | default (1.0) |
| diesel_ICE_ship | REAL: `cd.shipping_fuel_demand` (assumes all shipping=diesel) | default (inf) | manual: 0.75×5280/8760 |
| district_heating_grid | REAL (unconfirmed if index actually matches — likely near-zero) | REAL: `DH_potential.xlsx` share × max heat demand | REAL `_max_load_heat` (unconfirmed if index matches) |
| electrode_boiler | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_heat` |
| electrode_boiler_DH | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_district_heat` |
| electrolysis | REAL: Hydrogen Europe `extracted_capacity_additions.xlsx` | default (inf) | default (1.0) |
| fischer_tropsch | default (0) | default (inf) | default (1.0) |
| fuel_cell | default (0) | default (inf) | default (1.0) |
| gasification | default (0) | default (inf) | default (1.0) |
| haber_bosch | REAL: `cd.ammonia_demand` | default (inf) | default (1.0) |
| hard_coal_boiler_DH | REAL: `_existing_capacity_heat` | REAL coal-phaseout [flag]; else default (inf) | REAL coal-phaseout [flag]; **else stays default (never reaches district_heat branch)** |
| hard_coal_plant | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | REAL coal-phaseout [flag]; else default (inf) | REAL coal-phaseout [flag]; else JRC POTEnCIA technical-availability default |
| heat_pump | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_heat` |
| heat_pump_DH | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_district_heat` |
| hydrogen_FC_ship | default (0) | default (inf) | manual: 0.75×5280/8760 |
| hydrogen_to_cement_fuel | REAL: `_existing_capacity_cement_fuel` | default (inf) | default (1.0) |
| industrial_gas_consumer | REAL: `cd.industrial_gas_demand` [flag]; else default (0) | manual: forced ∞ | default (1.0) |
| lignite_coal_plant | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | REAL coal-phaseout [flag]; else default (inf) | REAL coal-phaseout [flag]; else JRC POTEnCIA default |
| lng_terminal | REAL: SciGrid LNG-terminal DB (+manual additions [flag]) | **REAL**, computed inline as existing×`lng_potential_increase` constant | [flag `ramp_up_lng`] constants-based ramp; else default (1.0) |
| methanation | default (0) | default (inf) | default (1.0) |
| methanol_ICE_ship | default (0) | default (inf) | manual: 0.75×5280/8760 |
| methanol_from_biomass | default (0) | default (inf) | default (1.0) |
| methanol_from_hydrogen | default (0) | default (inf) | default (1.0) |
| methanol_from_natural_gas | REAL: `cd.methanol_demand` | default (inf) | default (1.0) |
| natural_gas_boiler | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_heat` |
| natural_gas_boiler_DH | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_district_heat` |
| natural_gas_turbine | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | default (inf) | default = JRC POTEnCIA technical availability |
| nuclear | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | REAL: summed existing [flag] or manual 0/inf | REAL seasonal ENTSO-E [flag] or non-seasonal ENTSO-E average |
| oil_boiler | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_heat` |
| oil_boiler_DH | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_district_heat` |
| oil_plant | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | default (inf) | default = JRC POTEnCIA technical availability |
| oil_to_diesel_conversion | REAL: derived from ICE_diesel+HDT_diesel+shipping existing capacities [flag]; else default (0) | default (inf) | default (1.0) |
| oil_to_gasoline_conversion | REAL: derived from ICE_petrol existing capacity [flag]; else default (0) | default (inf) | default (1.0) |
| oil_to_kerosene_conversion | REAL: derived from `cd.kerosene_demand` [flag]; else default (0) | default (inf) | default (1.0) |
| oil_to_naphtha_conversion | **default (0) always — not in the flag-conditional list at all** | default (inf) | default (1.0) |
| olefin_from_methanol | default (0) | default (inf) | default (1.0) |
| olefin_from_naphtha | REAL: `cd.naphtha_demand`-derived | default (inf) | default (1.0) |
| photovoltaics | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | REAL: ENSPRESO solar potential (+manual CH/NO) | REAL: Antonini [flag] else renewables.ninja |
| pyrolysis | REAL: `biochar_existing.xlsx` | default (inf) | default (1.0) |
| refining | REAL: Energy Institute Statistical Review xlsx | default (inf) | default (1.0) |
| reservoir_hydro | REAL: JRC Hydro DB (HDAM) | REAL: = existing capacity summed by node | REAL: Tröndle reservoir capacity-factor dataset |
| run-of-river_hydro | REAL: JRC Hydro DB (HROR) | REAL: = existing capacity | REAL: Tröndle RoR capacity-factor dataset |
| waste_boiler_DH | REAL: `_existing_capacity_heat` | default (inf) | REAL: `_max_load_district_heat` |
| waste_plant | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | default (inf) | default = JRC POTEnCIA technical availability |
| waste_to_cement_fuel | REAL: `_existing_capacity_cement_fuel` | default (inf) | default (1.0) |
| wind_offshore | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | REAL: ENSPRESO offshore potential (+manual CH/NO) | REAL: renewables.ninja only (Antonini explicitly excluded) |
| wind_onshore | REAL: ENTSO-E+OPSD+IRENA (or BNEF) | REAL: ENSPRESO onshore potential (+manual CH/NO) | REAL: Antonini [flag] else renewables.ninja |
| natural_gas_turbine_CCS | REAL: IOGP CCS-database-derived (tech present in capture/cluster maps) | default (inf) | default (1.0) |
| biomass_plant_CCS | default (0) — tech absent from capture/cluster maps | default (inf) | default (1.0) |
| SMR_CCS | REAL: IOGP-derived (present in capture map) | default (inf) | default (1.0) |
| cement_post_comb | REAL: IOGP-derived (present in cluster map) | default (inf) | default (1.0) |
| BF_BOF_CCS | REAL: IOGP-derived (present in cluster map) | default (inf) | default (1.0) |
| NG_DRI_CCS | default (0) — tech absent from capture/cluster maps | default (inf) | default (1.0) |

---

## §4 — Conversion technologies: cost attributes (capex_specific_conversion, opex_specific_fixed, opex_specific_variable, carbon_intensity_technology)

`min_full_load_hours_fraction` has **no legacy equivalent at all** — stays at
framework default for all 76 technologies; there is nothing to port.
`carbon_intensity_technology` is **default (0) for almost everything** — the legacy
pipeline models combustion emissions as a *carrier*-level attribute
(`carbon_intensity_carrier_import`), not technology-level. Only 7 technologies get a
real/manual technology-level value (marked below).

Cost-DB agency abbreviations: **P**=Potencia, **D**=DIW, **T**=TYNDP, **DEA**=Danish
Energy Agency, **E**=EUREF, **L**=LUW — pooled (mean/median/min/max, one global
setting) across every agency that has a match, **no fallback priority order**.
**AddTech** = curated `costs_additional_technologies.xlsx` (separate from the 6
agencies, used when no agency has cost-DB coverage).

| Technology | capex_specific_conversion | opex_specific_fixed | opex_specific_variable | carbon_intensity_technology |
|---|---|---|---|---|
| BEV | REAL: vehicle_tech_parameters.csv | default (unit only) | REAL: vehicle_tech_parameters.csv | default |
| BF_BOF | REAL: AddTech xlsx | REAL: AddTech xlsx | manual: 392.16 | manual: total_emissions const − hard_coal CI×conv.factor |
| DAC | REAL: cost DB (DEA_ccs+LUW) | REAL: cost DB | REAL: cost DB | default |
| EAF | REAL: AddTech xlsx | REAL: AddTech xlsx | manual: 548.244 | manual: 0.01 |
| H2_DRI | REAL: AddTech xlsx | REAL: AddTech xlsx | manual: 340.2646 | manual: 0.01 |
| HDT_BET | REAL: HDT_params.xlsx | default (unit only) | REAL: HDT_params.xlsx | default |
| HDT_FCEV | REAL: HDT_params.xlsx | default | REAL: HDT_params.xlsx | default |
| HDT_diesel | REAL: HDT_params.xlsx | default | REAL: HDT_params.xlsx | default |
| ICE_diesel | REAL: vehicle_tech_parameters.csv | default | REAL: vehicle_tech_parameters.csv | default |
| ICE_petrol | REAL: vehicle_tech_parameters.csv | default | REAL: vehicle_tech_parameters.csv | default |
| NG_DRI | REAL: AddTech xlsx | REAL: AddTech xlsx | manual: 340.2646 (shared with H2_DRI) | manual: 0.01 |
| SMR | REAL: cost DB (LUW only) | REAL: cost DB | REAL: cost DB | default |
| ammonia_ICE_ship | REAL: AddTech xlsx | REAL: AddTech xlsx | default | default |
| anaerobic_digestion | REAL: cost DB (DEA_rf only) | REAL: cost DB | REAL: cost DB | default |
| biomass_boiler | REAL: cost DB (DEA_ih+LUW) | REAL: cost DB | REAL: cost DB | default |
| biomass_boiler_DH | REAL: cost DB (DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| biomass_plant | REAL: cost DB (P+D+E+L) | REAL: cost DB | REAL: cost DB | default |
| biomass_to_cement_fuel | manual: `get_capex_cement_fuel_retrofit` formula | default | default | default |
| biomethane_conversion | REAL: cost DB (DEA_rf only) | REAL: cost DB | REAL: cost DB | default |
| carbon_storage | REAL: AddTech xlsx | REAL: AddTech xlsx | manual: 4 Euro/tCO2eq | manual: −1 |
| cement_kiln | REAL: AddTech xlsx | REAL: AddTech xlsx | manual: 21.5 (ECRA) | manual: `clinker_carbon_intensity` |
| coal_to_cement_fuel | manual: `get_capex_cement_fuel_retrofit` | default | default | default |
| diesel_ICE_ship | REAL: AddTech xlsx | REAL: AddTech xlsx | default | default |
| district_heating_grid | manual: formula (heat-demand FLH × annualized capex + heat-exchanger capex) | default | manual: 1.5 Euro/MWh (DEA DH-transport report) | default |
| electrode_boiler | REAL: cost DB (DEA_ih+LUW) | REAL: cost DB | REAL: cost DB | default |
| electrode_boiler_DH | REAL: cost DB (DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| electrolysis | REAL: cost DB (DEA_rf+LUW) | REAL: cost DB | REAL: cost DB | default |
| fischer_tropsch | REAL: cost DB (DEA_rf+LUW) | REAL: cost DB | REAL: cost DB (DEA fopex "unclear") | default |
| fuel_cell | REAL: cost DB (P+D+DEA) | REAL: cost DB | REAL: cost DB | default |
| gasification | REAL: cost DB (DEA_rf only) | REAL: cost DB | REAL: cost DB | default |
| haber_bosch | REAL: cost DB (DEA_rf only) | REAL: cost DB | REAL: cost DB | default |
| hard_coal_boiler_DH | REAL: cost DB (E+L only) | REAL: cost DB | REAL: cost DB | default |
| hard_coal_plant | REAL: cost DB (P+D+DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| heat_pump | REAL: cost DB (DEA_ih+L) | REAL: cost DB | REAL: cost DB | default |
| heat_pump_DH | REAL: cost DB (DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| hydrogen_FC_ship | REAL: AddTech xlsx | REAL: AddTech xlsx | default | default |
| hydrogen_to_cement_fuel | manual: `get_capex_cement_fuel_retrofit` | default | default | default |
| industrial_gas_consumer | default | default | default | manual: `-1 × carbon_intensity_carrier_total["natural_gas"]` |
| lignite_coal_plant | REAL: cost DB (P+D+E) | REAL: cost DB | REAL: cost DB | default |
| lng_terminal | REAL: AddTech xlsx | REAL: AddTech xlsx | manual: elengy formula ≈2.5 Euro/MWh | default |
| methanation | REAL: cost DB (DEA_rf+L) | REAL: cost DB | REAL: cost DB | default |
| methanol_ICE_ship | REAL: AddTech xlsx | REAL: AddTech xlsx | default | default |
| methanol_from_biomass | REAL: cost DB (DEA_rf only) | REAL: cost DB | REAL: cost DB | default |
| methanol_from_hydrogen | REAL: cost DB (DEA_rf only) | REAL: cost DB | REAL: cost DB | default |
| methanol_from_natural_gas | REAL: AddTech xlsx | REAL: AddTech xlsx | default | default |
| natural_gas_boiler | REAL: cost DB (DEA_ih+L) | REAL: cost DB | REAL: cost DB | default |
| natural_gas_boiler_DH | REAL: cost DB (DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| natural_gas_turbine | REAL: cost DB (all 6 agencies) | REAL: cost DB | REAL: cost DB | default |
| nuclear | REAL: cost DB (P+D+E+L) | REAL: cost DB | REAL: cost DB | default |
| oil_boiler | REAL: cost DB (DEA_ih+L) | REAL: cost DB | REAL: cost DB | default |
| oil_boiler_DH | REAL: cost DB (DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| oil_plant | REAL: cost DB (P+D only) | REAL: cost DB | REAL: cost DB | default |
| oil_to_diesel_conversion | default | default | manual, conditional [flag `assume_oil_price_for_diesel_and_gasoline`]: BNEF diesel-vs-oil delta; else default | default |
| oil_to_gasoline_conversion | default | default | manual, conditional [flag]: BNEF gasoline-vs-oil delta; else default | default |
| oil_to_kerosene_conversion | default | default | default | default |
| oil_to_naphtha_conversion | default | default | default | default |
| olefin_from_methanol | REAL: AddTech xlsx | REAL: AddTech xlsx | default (commented-out manual value 17) | default |
| olefin_from_naphtha | REAL: AddTech xlsx | REAL: AddTech xlsx | default (commented-out manual value 55) | default |
| photovoltaics | REAL: cost DB (P+D+DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| pyrolysis | REAL: cost DB (DEA_rf only) | REAL: cost DB | REAL: cost DB | default |
| refining | default | manual: formula (1-2%×capex + staff cost) | manual: formula ($1/barrel) | default |
| reservoir_hydro | REAL: cost DB (P+D+E+L) | REAL: cost DB | REAL: cost DB | default |
| run-of-river_hydro | REAL: cost DB (P+D+E+L) | REAL: cost DB | REAL: cost DB | default |
| waste_boiler_DH | REAL: cost DB (DEA+E+L) | REAL: cost DB | REAL: cost DB | default |
| waste_plant | REAL: cost DB (P+E+L) | REAL: cost DB | REAL: cost DB | manual: forced 0 |
| waste_to_cement_fuel | manual: `get_capex_cement_fuel_retrofit` | default | default | default |
| wind_offshore | REAL: cost DB (all 6) | REAL: cost DB | REAL: cost DB | default |
| wind_onshore | REAL: cost DB (all 6) | REAL: cost DB | REAL: cost DB | default |
| natural_gas_turbine_CCS | REAL: cost DB delta vs base tech [flag-dependent, see §2 note] | same | same | default |
| biomass_plant_CCS | REAL: cost DB delta vs base tech [flag-dependent] | same | same | default |
| SMR_CCS | REAL: cost DB (DEA_ccs absolute) | same | same | default |
| cement_post_comb | REAL: cost DB (DEA_ccs absolute, base tech not in any agency DB) | same | same | default |
| BF_BOF_CCS | REAL: cost DB (DEA_ccs absolute, base tech not in DB) | same | same | default |
| NG_DRI_CCS | REAL: cost DB (DEA_ccs absolute, base tech not in DB) | same | same | default |

---

## §5 — Storage technologies: full attribute sourcing

Never touched by any code path for any of the 5 techs → stays at framework default:
`capacity_addition_min`, `capacity_addition_min_energy`, `capacity_investment_existing`
(+energy), `min_load`, `max_load` (+energy), `flow_storage_inflow`,
`opex_specific_fixed_energy`. `max_diffusion_rate` only via a global scenario flag.

| Technology | reference_carrier | lifetime | efficiency_charge/discharge | self_discharge | construction_time | capex_specific_storage (+energy) | opex_specific_fixed | capacity_existing (+energy) | capacity_limit (+energy) | energy_to_power_ratio_min/max |
|---|---|---|---|---|---|---|---|---|---|---|
| battery | REAL: JSON "electricity" | REAL: JSON = 13 | REAL: √0.86=0.927 each (Staffell 2019) | manual: 0.1% (ESM report) | REAL: JSON = 1 | REAL: `cost_storage.xlsx` DB | REAL: `cost_storage.xlsx` DB | REAL [flag `use_battery_existing_capacity`+`use_existing_capacities`]: BNEF Energy Storage Market Outlook; else default (0) | default (inf) unless global no-investment flag zeroes it | REAL 4/4 [flag `use_battery_e2p_ratio`]; else default |
| pumped_hydro | REAL: JSON "electricity" | REAL: JSON = 55; **REAL override → 200 [flag `use_200y_lifetime_hydro`]** | REAL: √0.78=0.883 each | manual: 0 (ESM report, explicit) | REAL: JSON = 3 | REAL: `cost_storage.xlsx` DB | REAL: `cost_storage.xlsx` DB | REAL: JRC Hydro DB "HPHS" apportioned via OPSD/PPSD commissioning years | REAL: = summed existing capacity per node (no further expansion) [if `allow_investment` & not `short_term_analysis`] | default |
| natural_gas_storage | REAL: JSON "natural_gas" | REAL: JSON = 100 | REAL: √0.995=0.9975 each | default (0, no manual branch) | REAL: JSON = 0 (numerically = default) | REAL but placeholder: JSON `0.0`/`0.0` ("fixed investment anyway") | **default — fallback branch is dead code** | REAL: IGGIELGNC1 gas-storage dataset (SciGrid/ENTSOG), filtered to active storages | manual: 0 ("no investment possible") | default |
| oil_storage | REAL: JSON "oil" | REAL: JSON = 100 | REAL: √0.995=0.9975 each | default (0, no manual branch) | REAL: JSON = 0 | REAL but placeholder: JSON `1`/`1` ("dummy tech, avoid over-installation") | default (dead fallback) | **default (0) — no extraction branch at all** | **default (inf) — no extraction, no manual override** | default |
| salt_cavern_storage | REAL: JSON "hydrogen" | REAL: JSON = 100 | REAL: √0.99=0.995 each | default (0, no manual branch) | REAL: JSON = 0 | REAL: `cost_storage.xlsx` DB (Victoria et al. 2022) | REAL: `cost_storage.xlsx` DB | **default (0) — no extraction branch** | **default (inf) — no manual override** | default |

**`pumped_hydro.py` current gap vs. this table**: only `reference_carrier` is correctly
ported; `lifetime` is a placeholder `25` (should be `55`, or `200` under the flag) —
wrong value, not just missing. `capacity_existing`, `capacity_limit`,
`efficiency_charge`/`efficiency_discharge` (currently silently `1.0`, physically
implausible), `capex_specific_storage`(+energy), `opex_specific_fixed`, and
`construction_time` are all still at framework default despite the legacy pipeline
having real data for every one of them.

---

## §6 — Transport technologies: full attribute sourcing

Never touched for any of the 5 techs → framework default: `capacity_addition_min`,
`capacity_investment_existing`, `distance` (computed generically elsewhere from edge
geometry, out of scope here — not a migration gap). `max_diffusion_rate` only via
global flag.

| Technology | reference_carrier | lifetime | transport_loss_factor_linear | capex_per_distance_transport | capacity_existing | capacity_limit | opex_specific_fixed | construction_time |
|---|---|---|---|---|---|---|---|---|
| power_line | REAL: JSON "electricity" | manual: 60 (Euro-Calliope) | manual: 5e-5 /km (Euro-Calliope) | REAL: AddTech xlsx "power_line" | REAL: ENTSO-E transmission capacity per edge/year | REAL [flag `use_power_line_capacity_limit`]: TYNDP2022 + IoSN candidate-units; else explicit inf | **default — fallback is dead code, no offshore entry exists** | default |
| natural_gas_pipeline | REAL: JSON "natural_gas" | manual: 60 (assumption; DEA suggests 50) | manual: 5e-5 /km | REAL: AddTech xlsx (overwrites an earlier manual TYNDP value — DB wins) | REAL: SciGrid/IGGIELGNC1 [flag] or ENTSOG/GIE `gasCapacitiesAggregated.csv` | **default (inf) — extractor only handles power_line** | default; **REAL per offshore edge [flag `account_for_offshore_transport`]** (AddTech "natural_gas_pipeline_offshore") | default |
| carbon_pipeline | REAL: JSON "carbon" | manual: 50 (DEA CO2 transport/storage catalogue) | **default — only the unit is set, value never written** | REAL: AddTech xlsx | **default (0) — no extraction branch** | **default (inf) — no extraction branch** | default; REAL per offshore edge [flag] | default |
| hydrogen_pipeline | REAL: JSON "hydrogen" | manual: 50 (ENS/Danish tech catalogue) | manual: 0.029/1000=2.9e-5 /km (ENS) | REAL: AddTech xlsx | **default (0) — no existing H2 network modeled** | **default (inf) — no extraction branch** | default; REAL per offshore edge [flag] | **manual: 1 — only transport tech with non-default construction_time** |
| oil_pipeline | REAL: JSON "oil" | manual: 60 (assumption; DEA suggests 50) | manual: 5e-5 /km | REAL: AddTech xlsx (overwrites earlier manual TYNDP value — DB wins) | **default (0) — extractor doesn't cover oil_pipeline** | **default (inf) — no extraction branch** | default; REAL per offshore edge [flag] | default |

**`power_line.py` current gap vs. this table**: `reference_carrier` correctly ported.
`_set_lifetime` doesn't even assign a value — stays `NaN` (should be `60`). Everything
else (`transport_loss_factor_linear`, `capacity_existing`, `capex_per_distance_transport`,
`capacity_limit`) is at framework default despite the legacy pipeline having real data
for `capacity_existing` (ENTSO-E) and `capex_per_distance_transport` (cost xlsx) at
minimum. The two biggest cross-cutting gaps for both `pumped_hydro` and `power_line`
today: **no cost data** and **no existing-capacity data** — both currently look like
greenfield technologies with zero installed base to the new framework.

---

## Sources consulted (for traceability, not exhaustive)
- `Input_data_creation/carriers.py`, `technology_data.py`, `conversion_technologies.py`, `storage_technologies.py`, `transport_technologies.py`, `constants.py`, `helpers.py`, `energy_system.py`
- `NUTS0_Source_Data/03-conversion_technologies/set_conversion_technologies.json`, `04-storage_technologies/set_storage_technologies.json`, `05-transport_technologies/set_transport_technologies.json`
- `NUTS0_Source_Data/04-storage_technologies/cost_storage.xlsx`, `02-Technologies/costs_additional_technologies.xlsx` (existence/coverage checks)
- Current `zen_europe` state: `elements/carriers/electricity.py`, `elements/carriers/biomass.py`, `elements/conversion_technologies/photovoltaics.py`, `elements/storage_technologies/pumped_hydro.py`, `elements/transport_technologies/power_line.py`, `datasets/datasets/carrier/enspreso.py`

---

## Flag glossary (footnote tags)
- [SHED] — generic catch-all at the end of set_manual_attributes: if allow_all_demand_shedding is enabled AND a carrier's price_shed_demand is still exactly np.inf after its own branch, it's reset to 1e4. Applies to essentially every "default(∞)" cell above.
- [ST] — behavior shown assumes short_term_analysis=False; flips to the alternate branch when True.
- [CAP] — _create_availability_coal/_create_availability_oil/_create_availability_waste only write a CSV if cap_coal_oil_import/cap_waste_import (→ availability_import.csv) or short_term_analysis/annual_cap_coal_oil_import (→ availability_import_yearly.csv) is set; if none are set, nothing is written at all for that carrier.
- [REF] — use_refining_sector flag (gasoline/diesel import=0 only if refineries modeled).
- [IND] — use_industrial_gas_demand (natural_gas_industry demand) / use_industrial_sector (hydrogen demand path).
- [BIO] — which of the 3 _create_availability_biomass branches fires depends on short_term_analysis, annual_cap_biomass_import, use_biomass_projections; table shows the use_biomass_projections=True (ENSPRESO) branch as "default" since that's what biomass.py's Enspreso.get_availability_import actually ports.
- [COAL2] — allow_hard_coal_export_emission_credit.

---

## Other notable findings
- POTEnCIA fallback is effectively dead code: get_carrier_identifier only returns non-None for hard_coal, natural_gas, uranium, lignite, oil, waste, biogas, biomass — and every one of those names is already caught by an earlier branch (BNEF or ENTSOE/TYNDP) in set_fuel_price_attributes, so the fuel_prices_potencia fallback (else: clause) is never actually reached for any real carrier name in this codebase under normal data availability.
- oil vs crude_oil split: oil (refined/heavy-oil equivalent, e.g. boiler fuel) and crude_oil (refinery feedstock) are priced from the same BNEF "oil" series but through two different code paths (oil via the generic bnef-index branch, crude_oil via its own unconditional elif) — worth preserving as two independent price sources during migration even though the number is identical today.
- 31, not 30, carrier names were listed in the request (I counted them explicitly); I covered all as given rather than guessing which to drop.