# ZEN-europe


Data for the European, sector-coupled energy system model.

ZEN-europe generates the input data of a European energy system model for
[ZEN-garden](https://github.com/ZEN-universe/ZEN-garden), built on
[ZEN-creator](https://zen-creator.readthedocs.io/en/latest/). It covers 28
countries at NUTS0 resolution and 15 sectors, from electricity and heat to
steel, cement, chemicals and transport.

## Quick start

```bash
conda env create -f zen_europe_env.yml
conda activate zen-europe-env

# generate the default dataset from the folder that contains data/raw_data
zen-europe

# generate every variant declared in a models file
zen-europe --config_path ./my_config.yaml --all
```

The dataset is written to `./data/<name>`, together with the ZEN-garden
configuration `./data/config.yaml`.

## Dashboard (beta)

`dashboard/` contains a web dashboard, in beta, to create datasets without
editing YAML files: configure model variants with an explanation for every
setting, inspect their sectors, technologies and carriers, generate and
download them, and explore the generated data in charts and maps.

```bash
pip install -e ".[dashboard]"
cd dashboard/frontend && npm install && npm run build   # once, needs Node.js
cd ../backend && python -m zen_dashboard                # http://127.0.0.1:8000
```

See [the dashboard page](docs/files/user_guide/dashboard.rst) of the
documentation for how to use it.

## Documentation

The documentation in `docs/` describes the design, the model structure, the
execution procedure, tutorials on settings and models files, and the rules
for adding elements and datasets.
