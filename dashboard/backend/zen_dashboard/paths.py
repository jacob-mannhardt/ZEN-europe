"""Where the dashboard reads ZEN-europe from and where it writes its own files.

ZEN-europe is only read: the configuration file and the raw data stay where
they are. Everything the dashboard writes (its models file, the generated
datasets and the logs) goes to the workspace folder, which defaults to
``dashboard/workspace`` and can be moved with the environment variable
``ZEN_DASHBOARD_WORKSPACE``.
"""

import logging
import os
from pathlib import Path

# importing the model creator registers ZEN-europe's settings, sectors and
# elements with ZEN-creator's registries
logging.getLogger("zen_creator").setLevel(logging.WARNING)
from zen_europe.model_creator import DEFAULT_CONFIG_PATH  # noqa: E402

DASHBOARD_ROOT = Path(__file__).resolve().parents[2]

# the root of the ZEN-europe repository; generation runs from there, since the
# configuration file resolves source_path relative to the working directory
ZEN_EUROPE_ROOT = DEFAULT_CONFIG_PATH.parent.parent

CONFIG_PATH = Path(os.environ.get("ZEN_EUROPE_CONFIG", DEFAULT_CONFIG_PATH)).resolve()

# the models file of ZEN-europe, used to seed the dashboard's own models file
ZEN_EUROPE_MODELS_PATH = CONFIG_PATH.parent / "models.yaml"

WORKSPACE = Path(
    os.environ.get("ZEN_DASHBOARD_WORKSPACE", DASHBOARD_ROOT / "workspace")
).resolve()
MODELS_PATH = WORKSPACE / "models.yaml"
OUTPUT_PATH = WORKSPACE / "created_models"
LOG_PATH = WORKSPACE / "logs"
META_PATH = WORKSPACE / "meta"
# the dataset of the default settings, which the datasets are compared with
REFERENCE_PATH = WORKSPACE / "reference"

FRONTEND_DIST = DASHBOARD_ROOT / "frontend" / "dist"


def ensure_workspace() -> None:
    """Create the workspace folders."""
    for path in (WORKSPACE, OUTPUT_PATH, LOG_PATH, META_PATH, REFERENCE_PATH):
        path.mkdir(parents=True, exist_ok=True)
