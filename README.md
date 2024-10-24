# Supramolecular Explorer

## Installation

Create an isolated environment and install the package.

```
python -m venv venv
venv/Scripts/activate    # on Windows
source venv/bin/activate # on Linux
python -m pip install --find-links wheels .
```

## Development

Default linting settings and formatting settings (using [`ruff`](https://docs.astral.sh/ruff/)) have been created within `pyproject.toml` and will
be applied if the optional dependencies have been installed. Editable install
(`-e`) is recommended for code development and `pre-commit` should take care of code consistency when contributing.

```
python -m pip install -e --find-links wheels .[dev]
pre-commit install
```