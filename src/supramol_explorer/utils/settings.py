"""Constants loaded from the environment configuration."""

import tomllib
from pathlib import Path

# Load all settings.
SETTINGS_PATH = Path(".env.toml")

if not SETTINGS_PATH.exists():
    SETTINGS_PATH = Path("settings.toml")
    if not SETTINGS_PATH.exists():
        raise RuntimeError("Settings must be in .env.toml or settings.toml!")

with open(SETTINGS_PATH, "rb") as f:
    SETTINGS = tomllib.load(f)
