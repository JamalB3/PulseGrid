import pandas as pd

from processing.silver_processor import (
    identify_invalid_events,
    prepare_dataframe,
)


def build_valid_event() -> dict:
    return {
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


def test_valid_event_is_not_rejected():
    dataframe = pd.DataFrame([build_valid_event()])

    prepared = prepare_dataframe(dataframe)
    invalid_mask = identify_invalid_events(prepared)

    assert invalid_mask.iloc[0] == False


def test_invalid_temperature_is_rejected():
    event = build_valid_event()
    event["temperature"] = 999.0

    dataframe = pd.DataFrame([event])

    prepared = prepare_dataframe(dataframe)
    invalid_mask = identify_invalid_events(prepared)

    assert invalid_mask.iloc[0] == True


def test_missing_device_id_is_rejected():
    event = build_valid_event()
    event["device_id"] = None

    dataframe = pd.DataFrame([event])

    prepared = prepare_dataframe(dataframe)
    invalid_mask = identify_invalid_events(prepared)

    assert invalid_mask.iloc[0] == True


def test_negative_energy_usage_is_rejected():
    event = build_valid_event()
    event["energy_usage"] = -5.0

    dataframe = pd.DataFrame([event])

    prepared = prepare_dataframe(dataframe)
    invalid_mask = identify_invalid_events(prepared)

    assert invalid_mask.iloc[0] == True


def test_duplicate_event_ids_can_be_removed():
    event = build_valid_event()

    dataframe = pd.DataFrame([
        event,
        event.copy(),
    ])

    prepared = prepare_dataframe(dataframe)
    invalid_mask = identify_invalid_events(prepared)

    valid_dataframe = prepared[~invalid_mask].copy()

    deduplicated = valid_dataframe.drop_duplicates(
        subset=["event_id"],
        keep="first",
    )

    assert len(valid_dataframe) == 2
    assert len(deduplicated) == 1