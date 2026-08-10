import json

import pandas as pd

from processing.silver_processor import (
    identify_invalid_events,
    load_bronze_events,
    prepare_dataframe,
)


def test_bronze_records_can_be_loaded_and_validated(tmp_path):
    bronze_file = tmp_path / "telemetry.jsonl"

    valid_event = {
        "event_id": "event_001",
        "device_id": "sensor_0001",
        "building_id": "building_miami_hq",
        "building": "Miami HQ",
        "floor": 1,
        "room_id": "miami_1_server",
        "room": "Server Room",
        "room_type": "server_room",
        "timestamp": "2026-08-10T12:00:00+00:00",
        "temperature": 72.0,
        "humidity": 40.0,
        "energy_usage": 5.0,
        "air_quality": 30,
        "occupancy": 1,
    }

    invalid_event = valid_event.copy()
    invalid_event["event_id"] = "event_002"
    invalid_event["temperature"] = 999.0

    with bronze_file.open("w", encoding="utf-8") as file:
        file.write(json.dumps(valid_event) + "\n")
        file.write(json.dumps(invalid_event) + "\n")

    dataframe = load_bronze_events(bronze_file)
    prepared = prepare_dataframe(dataframe)
    invalid_mask = identify_invalid_events(prepared)

    assert len(prepared) == 2
    assert invalid_mask.sum() == 1