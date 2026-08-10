from generator.device_loader import load_devices


def test_load_devices_returns_devices():
    devices = load_devices()

    assert len(devices) > 0


def test_devices_contain_required_fields():
    devices = load_devices()

    required_fields = {
        "device_id",
        "building_id",
        "building",
        "floor",
        "room_id",
        "room",
        "room_type",
        "temperature_range",
        "humidity_range",
        "energy_range",
        "air_quality_range",
        "occupancy_range",
    }

    for device in devices:
        assert required_fields.issubset(device.keys())


def test_device_ids_are_unique():
    devices = load_devices()

    device_ids = [
        device["device_id"]
        for device in devices
    ]

    assert len(device_ids) == len(set(device_ids))