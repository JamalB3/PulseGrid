import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIRECTORY = PROJECT_ROOT / "data" / "bronze"
BRONZE_FILE = BRONZE_DIRECTORY / "telemetry.jsonl"


def write_event(event: dict[str, Any]) -> None:
    """Append one raw telemetry event to the Bronze JSONL file."""

    BRONZE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with BRONZE_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event))
        file.write("\n")