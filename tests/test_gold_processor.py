import pandas as pd

from analytics.gold_processor import (
    DEVICE_OFFLINE_MINUTES,
    TEMPERATURE_ALERT_THRESHOLD,
    build_device_health,
    build_hourly_metrics,
    build_location_metrics,
)

def build_test_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_id": "event_001",
                "device_id": "sensor_0001",
                "building_id": "building_miami_hq",
                "building": "Miami HQ",
                "floor": 1,
                "room_id": "miami_1_server",
                "room": "Server Room",
                "room_type": "server_room",
                "timestamp": pd.Timestamp(
                    "2026-08-18T12:00:00Z"
                ),
                "temperature": 70.0,
                "humidity": 40.0,
                "energy_usage": 2.0,
                "air_quality": 30,
                "occupancy": 1,
            },
            {
                "event_id": "event_002",
                "device_id": "sensor_0001",
                "building_id": "building_miami_hq",
                "building": "Miami HQ",
                "floor": 1,
                "room_id": "miami_1_server",
                "room": "Server Room",
                "room_type": "server_room",
                "timestamp": pd.Timestamp(
                    "2026-08-18T12:30:00Z"
                ),
                "temperature": 74.0,
                "humidity": 50.0,
                "energy_usage": 4.0,
                "air_quality": 40,
                "occupancy": 3,
            },
        ]
    )


def test_location_metrics_calculates_correct_aggregations():
    dataframe = build_test_dataframe()

    result = build_location_metrics(dataframe)

    assert len(result) == 1

    row = result.iloc[0]

    assert row["total_events"] == 2
    assert row["unique_devices"] == 1

    assert row["average_temperature"] == 72.0
    assert row["maximum_temperature"] == 74.0

    assert row["average_humidity"] == 45.0

    assert row["total_energy_usage"] == 6.0
    assert row["average_energy_usage"] == 3.0

    assert row["average_air_quality"] == 35.0

    assert row["average_occupancy"] == 2.0
    assert row["maximum_occupancy"] == 3


def test_hourly_metrics_groups_events_into_same_hour():
    dataframe = build_test_dataframe()

    result = build_hourly_metrics(dataframe)

    assert len(result) == 1

    row = result.iloc[0]

    assert row["event_hour"] == pd.Timestamp(
        "2026-08-18T12:00:00Z"
    )

    assert row["event_count"] == 2
    assert row["average_temperature"] == 72.0
    assert row["average_humidity"] == 45.0
    assert row["total_energy_usage"] == 6.0
    assert row["average_air_quality"] == 35.0
    assert row["average_occupancy"] == 2.0


def test_device_health_calculates_device_metrics():
    dataframe = build_test_dataframe()

    result = build_device_health(dataframe)

    assert len(result) == 1

    row = result.iloc[0]

    assert row["device_id"] == "sensor_0001"
    assert row["total_events"] == 2

    assert row["last_event_timestamp"] == pd.Timestamp(
        "2026-08-18T12:30:00Z"
    )

    assert row["average_temperature"] == 72.0
    assert row["maximum_temperature"] == 74.0
    assert row["average_energy_usage"] == 3.0

    assert row["minutes_since_last_event"] == 0.0
    assert row["device_status"] == "online"


def test_device_health_identifies_offline_device():
    dataframe = build_test_dataframe()

    older_event = dataframe.iloc[0].copy()

    older_event["event_id"] = "event_003"
    older_event["device_id"] = "sensor_0002"
    older_event["room_id"] = "miami_1_office"
    older_event["room"] = "Office"
    older_event["room_type"] = "office"

    latest_timestamp = dataframe["timestamp"].max()

    older_event["timestamp"] = (
    latest_timestamp - pd.Timedelta(minutes=DEVICE_OFFLINE_MINUTES + 1)
    )

    dataframe = pd.concat(
        [
            dataframe,
            pd.DataFrame([older_event]),
        ],
        ignore_index=True,
    )

    result = build_device_health(dataframe)

    sensor_2 = result[
        result["device_id"] == "sensor_0002"
    ].iloc[0]

    assert sensor_2["minutes_since_last_event"] == DEVICE_OFFLINE_MINUTES + 1
    assert sensor_2["device_status"] == "offline"


def test_normal_temperature_does_not_trigger_alert():
    dataframe = build_test_dataframe()

    dataframe["temperature"] = TEMPERATURE_ALERT_THRESHOLD

    result = build_device_health(dataframe)

    row = result.iloc[0]

    assert bool(row["temperature_alert"]) is False


def test_high_temperature_triggers_alert():
    dataframe = build_test_dataframe()

    dataframe.loc[0, "temperature"] = (
        TEMPERATURE_ALERT_THRESHOLD + 1
    )

    result = build_device_health(dataframe)

    row = result.iloc[0]

    assert bool(row["temperature_alert"]) is True