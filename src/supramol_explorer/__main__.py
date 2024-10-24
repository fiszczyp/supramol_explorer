"""Package-level entry point for the Supramolecular Explorer."""

import logging
from pathlib import Path

from sqlalchemy import create_engine

from supramol_explorer.utils.settings import (
    SETTINGS,
    SETTINGS_PATH,
)

logging.captureWarnings(True)
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=SETTINGS["logger"]["level"],
    filename=Path(SETTINGS["logger"]["path"]),
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s (%(name)s)",
    datefmt="%d-%b-%y %H:%M:%S",
)

if __name__ == "__main__":
    logger.info(f"Starting code in {__name__}.")
    logger.info(f"Loaded settings from {SETTINGS_PATH.name}.")
    engine = create_engine(f"sqlite:////{SETTINGS["paths"]["database"]}")
