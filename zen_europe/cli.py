import logging

COLOR_SUCCESS = "\033[92m"
COLOR_WARNING = "\033[38;5;208m"  # orange
COLOR_RESET = "\033[0m"


class _ColorFormatter(logging.Formatter):
    """Formatter that colors WARNING-level records orange."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if record.levelno == logging.WARNING:
            return f"{COLOR_WARNING}{message}{COLOR_RESET}"
        return message


_handler = logging.StreamHandler()
_handler.setFormatter(_ColorFormatter("%(levelname)s - %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_handler])
logger = logging.getLogger(__name__)

import argparse
from pathlib import Path

from zen_europe.model_creator import create_model


def zen_europe_cli() -> None:
    parser = argparse.ArgumentParser(description="Run the ZEN Europe model")
    parser.add_argument(
        "--config",
        type=Path,
        required=False,
        default=None,
        help="Path to the model configuration file.",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=False,
        default="zen-europe",
        help="Name of the model that will be used when saving.",
    )
    parser.add_argument(
        "--output-folder",
        type=Path,
        required=False,
        default=".",
        help="Output directory to which the model will be saved.",
    )
    args = parser.parse_args()

    logger.info(f"Generating model '{args.name}' ...")
    create_model(config=args.config, name=args.name, output_folder=args.output_folder)
    path = (args.output_folder / args.name).resolve()
    logger.info(
        COLOR_SUCCESS + 
        f"Successfully generated model '{args.name}' and saved to {path}/" +
        COLOR_RESET)

