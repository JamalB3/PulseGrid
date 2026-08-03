import json
from typing import Any

from core.config import BRONZE_DIRECTORY, BRONZE_FILE


def write_event(event: dict[str, Any]) -> None:
    """Append one raw telemetry event to the Bronze JSONL file."""

    BRONZE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with BRONZE_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event))
        file.write("\n")