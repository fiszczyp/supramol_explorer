"""Writing to database."""

import json
from pathlib import Path


def read_json(infile: Path) -> int:
    """Read JSON file.

    Arguments
    ---------
    infile
        Path to the input file.

    Returns
    -------
        Content of the file.

    """
    with infile.open() as f:
        text = json.load(f)

    return text + "TEST"
