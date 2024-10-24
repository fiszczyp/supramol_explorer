# Supramolecular Explorer

## Installation

Create an isolated environment (with `venv` or `conda`):

```
python -m venv venv
venv/Scripts/activate    # on Windows
source venv/bin/activate # on Linux
python -m pip install --find-links wheels .
```

## TopSpin Requirements

Analysis of the NMR data requires the official TopSpin API, which comes shipped
with TopSpin 4.2.0+ and can be obtained free-of-charge for
[academic users](https://www.bruker.com/en/products-and-solutions/mr/nmr-software/topspin.html)
(exact API version might need updating based on the local configuration):

```
cd <TopSpin-installation-folder>/python/examples
python -m pip install ts_remote_api-2.0.0-py3-none-any.whl
python -m pip install bruker_nmr_api-1.3.5-py3-none-any.whl
python -m pip install -r requirements.txt
```

Only now the package will install correctly.


## Development

Default linting settings and formatting settings (using [`ruff`](https://docs.astral.sh/ruff/)) have been created within `pyproject.toml` and will
be applied if the optional dependencies have been installed. Editable install
(`-e`) is recommended for code development and `pre-commit` should take care of code consistency when contributing.

```
python -m pip install -e --find-links wheels .[dev]
pre-commit install
```