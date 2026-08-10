from generator.device_loader import load_devices
from generator.device_simulator import (
    SIMULATION_CONFIG,
    generate_normal_telemetry,
    generate_telemetry,
    inject_anomaly,
)


def test_generated_telemetry_contains_required_fields():
    device = load_devices()[0]

    event = generate_telemetry(device)

    required_fields = {
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
    }

    assert required_fields.issubset(event.keys())


def test_generated_telemetry_preserves_device_identity():
    device = load_devices()[0]

    event = generate_telemetry(device)

    assert event["device_id"] == device["device_id"]
    assert event["building_id"] == device["building_id"]
    assert event["room_id"] == device["room_id"]


def test_generated_event_has_unique_event_id():
    device = load_devices()[0]

    first_event = generate_telemetry(device)
    second_event = generate_telemetry(device)

    assert first_event["event_id"] != second_event["event_id"]



def test_normal_temperature_is_within_configured_range():
    device = load_devices()[0]

    event = generate_normal_telemetry(device)

    minimum, maximum = device["temperature_range"]

    assert minimum <= event["temperature"] <= maximum


def test_normal_humidity_is_within_configured_range():
    device = load_devices()[0]

    event = generate_normal_telemetry(device)

    minimum, maximum = device["humidity_range"]

    assert minimum <= event["humidity"] <= maximum


def test_normal_energy_usage_is_within_configured_range():
    device = load_devices()[0]

    event = generate_normal_telemetry(device)

    minimum, maximum = device["energy_range"]

    assert minimum <= event["energy_usage"] <= maximum


def test_normal_air_quality_is_within_configured_range():
    device = load_devices()[0]

    event = generate_normal_telemetry(device)

    minimum, maximum = device["air_quality_range"]

    assert minimum <= event["air_quality"] <= maximum


def test_normal_occupancy_is_within_configured_range():
    device = load_devices()[0]

    event = generate_normal_telemetry(device)

    minimum, maximum = device["occupancy_range"]

    assert minimum <= event["occupancy"] <= maximum



def test_invalid_temperature_anomaly(monkeypatch):
    device = load_devices()[0]
    event = generate_normal_telemetry(device)

    monkeypatch.setattr(
        "generator.device_simulator.random.random",
        lambda: 0.0,
    )

    anomalous_event = inject_anomaly(event)

    assert anomalous_event["temperature"] == 999.0


def test_anomaly_does_not_modify_original_event(monkeypatch):
    device = load_devices()[0]
    original_event = generate_normal_telemetry(device)

    original_temperature = original_event["temperature"]

    monkeypatch.setattr(
        "generator.device_simulator.random.random",
        lambda: 0.0,
    )

    anomalous_event = inject_anomaly(original_event)

    assert anomalous_event["temperature"] == 999.0
    assert original_event["temperature"] == original_temperature


def test_missing_humidity_anomaly(monkeypatch):
    device = load_devices()[0]
    event = generate_normal_telemetry(device)

    invalid_temperature = SIMULATION_CONFIG[
        "invalid_temperature_probability"
    ]
    missing_humidity = SIMULATION_CONFIG[
        "missing_humidity_probability"
    ]

    anomaly_roll = invalid_temperature + (missing_humidity / 2)

    monkeypatch.setattr(
        "generator.device_simulator.random.random",
        lambda: anomaly_roll,
    )

    anomalous_event = inject_anomaly(event)

    assert anomalous_event["humidity"] is None


def test_missing_device_id_anomaly(monkeypatch):
    device = load_devices()[0]
    event = generate_normal_telemetry(device)

    invalid_temperature = SIMULATION_CONFIG[
        "invalid_temperature_probability"
    ]
    missing_humidity = SIMULATION_CONFIG[
        "missing_humidity_probability"
    ]
    missing_device = SIMULATION_CONFIG[
        "missing_device_id_probability"
    ]

    anomaly_roll = (
        invalid_temperature
        + missing_humidity
        + (missing_device / 2)
    )

    monkeypatch.setattr(
        "generator.device_simulator.random.random",
        lambda: anomaly_roll,
    )

    anomalous_event = inject_anomaly(event)

    assert anomalous_event["device_id"] is None


def test_negative_energy_anomaly(monkeypatch):
    device = load_devices()[0]
    event = generate_normal_telemetry(device)

    invalid_temperature = SIMULATION_CONFIG[
        "invalid_temperature_probability"
    ]
    missing_humidity = SIMULATION_CONFIG[
        "missing_humidity_probability"
    ]
    missing_device = SIMULATION_CONFIG[
        "missing_device_id_probability"
    ]
    negative_energy = SIMULATION_CONFIG[
        "negative_energy_probability"
    ]

    anomaly_roll = (
        invalid_temperature
        + missing_humidity
        + missing_device
        + (negative_energy / 2)
    )

    monkeypatch.setattr(
        "generator.device_simulator.random.random",
        lambda: anomaly_roll,
    )

    anomalous_event = inject_anomaly(event)

    assert anomalous_event["energy_usage"] == -5.0


def test_no_anomaly_preserves_event(monkeypatch):
    device = load_devices()[0]
    event = generate_normal_telemetry(device)

    monkeypatch.setattr(
        "generator.device_simulator.random.random",
        lambda: 0.999999,
    )

    result = inject_anomaly(event)

    assert result == event
    assert result is not event