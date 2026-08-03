import json
from pathlib import Path
from typing import Any

import pandas as pd

from core.config import (
    BRONZE_FILE,
    MAX_AIR_QUALITY,
    MAX_HUMIDITY,
    MAX_TEMPERATURE,
    MIN_AIR_QUALITY,
    MIN_ENERGY_USAGE,
    MIN_HUMIDITY,
    MIN_OCCUPANCY,
    MIN_TEMPERATURE,
    REJECTED_FILE,
    SILVER_DIRECTORY,
    SILVER_FILE,
)


REQUIRED_COLUMNS = [
    "event_id",
    "device_id",
    "building_id",
    "building",
    "floor",
    "room_id",
    "room",
    "room_type",
    "timestamp",
    "temperature",
    "humidity",
    "energy_usage",
    "air_quality",
    "occupancy",
]


def load_bronze_events(file_path: Path) -> pd.DataFrame:
    """Load raw JSONL events from the Bronze layer."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Bronze file not found: {file_path}"
        )

    events: list[dict[str, Any]] = []

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)
                event["_source_line"] = line_number
                events.append(event)

            except json.JSONDecodeError:
                events.append(
                    {
                        "_source_line": line_number,
                        "_parse_error": True,
                        "_raw_record": line,
                    }
                )

    return pd.DataFrame(events)


def prepare_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add missing columns and convert values to appropriate data types."""

    dataframe = dataframe.copy()

    for column in REQUIRED_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = None

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
        utc=True,
    )

    numeric_columns = [
        "temperature",
        "humidity",
        "energy_usage",
        "air_quality",
        "occupancy",
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    return dataframe


def identify_invalid_events(dataframe: pd.DataFrame) -> pd.Series:
    """Return a Boolean mask identifying invalid telemetry records."""

    missing_required_values = dataframe[REQUIRED_COLUMNS].isna().any(axis=1)

    invalid_temperature = ~dataframe["temperature"].between(
        MIN_TEMPERATURE,
        MAX_TEMPERATURE,
    )

    invalid_humidity = ~dataframe["humidity"].between(
        MIN_HUMIDITY,
        MAX_HUMIDITY,
    )

    invalid_energy = dataframe["energy_usage"] < MIN_ENERGY_USAGE

    invalid_air_quality = ~dataframe["air_quality"].between(
        MIN_AIR_QUALITY,
        MAX_AIR_QUALITY,
    )

    invalid_occupancy = dataframe["occupancy"] < MIN_OCCUPANCY

    parse_error = dataframe.get(
        "_parse_error",
        pd.Series(False, index=dataframe.index),
    ).fillna(False)

    return (
        missing_required_values
        | invalid_temperature
        | invalid_humidity
        | invalid_energy
        | invalid_air_quality
        | invalid_occupancy
        | parse_error
    )


def write_rejected_events(dataframe: pd.DataFrame) -> None:
    """Write invalid records to a quarantine JSONL file."""

    SILVER_DIRECTORY.mkdir(parents=True, exist_ok=True)

    records = dataframe.to_dict(orient="records")

    with REJECTED_FILE.open("w", encoding="utf-8") as file:
        for record in records:
            serialized_record = {}

            for key, value in record.items():
                if pd.isna(value):
                    serialized_record[key] = None
                elif isinstance(value, pd.Timestamp):
                    serialized_record[key] = value.isoformat()
                else:
                    serialized_record[key] = value

            file.write(json.dumps(serialized_record))
            file.write("\n")


def build_silver_layer() -> None:
    """Clean Bronze events and write validated Silver data."""

    bronze_dataframe = load_bronze_events(BRONZE_FILE)
    prepared_dataframe = prepare_dataframe(bronze_dataframe)

    total_records = len(prepared_dataframe)

    invalid_mask = identify_invalid_events(prepared_dataframe)

    rejected_dataframe = prepared_dataframe[invalid_mask].copy()
    valid_dataframe = prepared_dataframe[~invalid_mask].copy()

    records_before_deduplication = len(valid_dataframe)

    valid_dataframe = valid_dataframe.drop_duplicates(
        subset=["event_id"],
        keep="first",
    )

    duplicates_removed = (
        records_before_deduplication - len(valid_dataframe)
    )

    valid_dataframe = valid_dataframe.sort_values("timestamp")

    output_columns = REQUIRED_COLUMNS + ["_source_line"]
    valid_dataframe = valid_dataframe[output_columns]

    SILVER_DIRECTORY.mkdir(parents=True, exist_ok=True)

    valid_dataframe.to_parquet(
        SILVER_FILE,
        index=False,
        engine="pyarrow",
    )

    write_rejected_events(rejected_dataframe)

    print("Silver processing complete.")
    print(f"Bronze records: {total_records}")
    print(f"Rejected records: {len(rejected_dataframe)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Silver records: {len(valid_dataframe)}")
    print(f"Silver file: {SILVER_FILE}")
    print(f"Quarantine file: {REJECTED_FILE}")


if __name__ == "__main__":
    build_silver_layer()