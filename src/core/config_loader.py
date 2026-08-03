import json
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> Any:
    """Load and return data from a JSON configuration file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in configuration file: {file_path}"
        ) from error