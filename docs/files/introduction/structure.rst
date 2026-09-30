.. _structure.structure:

###########################
Model Structure
###########################

This page gives an overview of the energy system that ZEN-europe describes
with its default settings. Every property listed here can be changed through
the settings (see :ref:`tutorials.tutorials`).


Spatial resolution
==================

ZEN-europe resolves Europe at the level of countries (NUTS0 regions). The
default set of nodes contains 28 countries:

- 25 member states of the European Union (all except Cyprus and Malta):
  AT, BE, BG, CZ, DE, DK, EE, EL, ES, FI, FR, HR, HU, IE, IT, LT, LU, LV, NL,
  PL, PT, RO, SE, SI, SK
- Switzerland (CH), Norway (NO) and the United Kingdom (UK)

The country codes follow the Eurostat convention (``EL`` for Greece, ``UK`` for
the United Kingdom). The nodes are set by ``region.set_nodes``.

Edges connect neighboring countries. They are derived from the adjacency of
the NUTS regions and from the TYNDP grid data, complemented by the
connections NO-FR and NO-BE (gas) and SE-LT (electricity). Every transport
technology (power lines, pipelines) uses this set of edges.


Temporal resolution
===================

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Setting
     - Default
     - Meaning
   * - ``time.reference_year``
     - 2022
     - First optimized year
   * - ``time.last_year``
     - 2050
     - Last year of the horizon
   * - ``time.interval_between_years``
     - 4
     - Years between two optimized years
   * - ``time.year_time_series``
     - 2019
     - Weather and demand year of the hourly time series

With the defaults, ZEN-garden optimizes the years 2022, 2026, ..., 2050. The
number of optimized years is derived from these settings. The hourly time
series can be aggregated by ZEN-garden, which is configured in the ``system``
block of the configuration file.


Scope of the energy system
==========================

ZEN-europe covers the supply, conversion, storage and transport of energy and
materials in all energy-intensive sectors. Demands are given as exogenous
time series per country (electricity, heat, passenger and
freight mileage, steel, cement, ammonia, methanol, olefins, fuels for aviation
and shipping). The model decides on the investment in and operation of all
technologies that supply these demands.

System-wide constraints and assumptions are set by the energy system class
``energy_system_nuts0``:

- a cumulative carbon emission budget, derived from a global budget for a
  given temperature target (default: 1.5°C at 50% likelihood)
  , optionally combined with or replaced by annual emission limits
- a discount rate of 5%

Base units of the dataset are hours, GW, km, megatons, million Euro, kilotons
of CO2, million vehicle-km, million tonne-km and kilotons of product.


Sectors
=======

Elements are grouped into sectors. A sector lists the technologies and carriers
that belong to it and the sectors it cannot exist without. The default
dataset includes all 15 sectors.

.. list-table::
   :header-rows: 1
   :widths: 22 48 30

   * - Sector
     - Content
     - Requires
   * - ``electricity``
     - Electricity generation, storage and transmission
     -
   * - ``gas``
     - Natural gas import, storage and transport
     -
   * - ``cement``
     - Cement clinker production
     -
   * - ``heat``
     - Decentralized heat generation
     - electricity
   * - ``district_heating``
     - District heating generation and grid
     - heat, electricity
   * - ``carbon``
     - Carbon capture, transport and storage
     - electricity, heat
   * - ``hydrogen``
     - Hydrogen production, storage and transport, and its direct derivatives
     - electricity, heat, district_heating
   * - ``ammonia``
     - Ammonia production and transport
     - electricity, hydrogen
   * - ``refining``
     - Crude oil refining into gasoline, diesel, naphtha and kerosene
     - hydrogen
   * - ``methanol``
     - Methanol and olefin production and transport
     - electricity, district_heating, hydrogen, refining
   * - ``aviation``
     - Aviation fuel demand
     - refining
   * - ``shipping``
     - Shipping fuel demand, split by fuel technology
     - electricity, hydrogen
   * - ``steel``
     - Primary and secondary steel production
     - electricity
   * - ``passenger_transport``
     - Passenger vehicle transport demand
     - electricity
   * - ``truck_transport``
     - Truck freight transport demand
     - electricity

Some technologies connect two sectors. They are declared by every sector they
belong to and are only part of the model when all of these sectors are
included. For example, ``natural_gas_turbine_CCS`` is declared by the
``electricity`` and the ``carbon`` sector, so a model without the ``carbon``
sector has no gas turbines with carbon capture.


Elements
========

The element library of ZEN-europe contains:

.. list-table::
   :header-rows: 1
   :widths: 50 20

   * - Element type
     - Number
   * - Carriers
     - 30
   * - Conversion technologies
     - 66
   * - Retrofitting technologies
     - 6
   * - Storage technologies
     - 6
   * - Transport technologies
     - 8

Each element is a class in ``zen_europe/elements/<element type>/``. The class
name and the ``name`` attribute identify the element, for example
``Photovoltaics`` with ``name = "photovoltaics"``.


Code layout
===========

.. code-block:: text

   zen_europe/
     cli.py                  command line interface
     model_creator.py        create_model(): settings, build, scenarios, write
     global_scenarios.py     system-, analysis-, solver- and set-wide scenarios
     settings/
       config.yaml           default configuration file
       <category>.py         one settings category per file
     elements/
       energy_systems/       the energy system (nodes, edges, carbon budget, ...)
       sectors/              one sector per file
       carriers/             one carrier per file
       conversion_technologies/
       retrofitting_technologies/
       storage_technologies/
       transport_technologies/
     datasets/
       datasets/             one data source per file
         energy_system/
         carrier/
         technology/
         financial/
       dataset_collections/  combinations of several data sources
     utils/                  helper functions shared by datasets

The raw data is not part of the repository. By default it is read from
``./data/raw_data`` relative to the working directory, with the subfolders
``01-energy_system``, ``02-carrier``, ``03-technology`` and ``04-monetary``.
