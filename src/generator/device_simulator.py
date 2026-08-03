import json
import random
import time
from datetime import datetime, timezone
from typing import Any
from generator.file_writer import write_event
from uuid import uuid4
from core.config import SIMULATION_FILE
from core.config_loader import load_json
from generator.device_loader import load_devices
from generator.file_writer import write_event


DEVICES = load_devices()
SIMULATION_CONFIG = load_json(SIMULATION_FILE)


def random_decimal(value_range: tuple[float, float]) -> float:
    """Generate a rounded decimal within the provided range."""

    minimum, maximum = value_range
    return round(random.uniform(minimum, maximum), 2)


def generate_telemetry(device: dict[str, Any]) -> dict[str, Any]:
    """Generate one realistic telemetry event."""

    event = {
        "event_id": str(uuid4()),
        "device_id": device["device_id"],
        "building_id": device["building_id"],
        "building": device["building"],
        "floor": device["floor"],
        "room_id": device["room_id"],
        "room": device["room"],
        "room_type": device["room_type"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": random_decimal(device["temperature_range"]),
        "humidity": random_decimal(device["humidity_range"]),
        "energy_usage": random_decimal(device["energy_range"]),
        "air_quality": random.randint(*device["air_quality_range"]),
        "occupancy": random.randint(*device["occupancy_range"]),
    }

    anomaly_roll = random.random()

    invalid_temperature_limit = (
        SIMULATION_CONFIG["invalid_temperature_probability"]
    )

    missing_humidity_limit = (
        invalid_temperature_limit
        + SIMULATION_CONFIG["missing_humidity_probability"]
    )

    missing_device_limit = (
        missing_humidity_limit
        + SIMULATION_CONFIG["missing_device_id_probability"]
    )

    negative_energy_limit = (
        missing_device_limit
        + SIMULATION_CONFIG["negative_energy_probability"]
    )

    if anomaly_roll < invalid_temperature_limit:
        event["temperature"] = 999.0
    elif anomaly_roll < missing_humidity_limit:
        event["humidity"] = None
    elif anomaly_roll < missing_device_limit:
        event["device_id"] = None
    elif anomaly_roll < negative_energy_limit:
        event["energy_usage"] = -5.0

    return event

def main() -> None:
    """Continuously generate and store simulated IoT telemetry."""

    print("Starting IoT device simulator...")
    print("Press Control + C to stop.\n")

    previous_event = None

    try:
        while True:
            device = random.choice(DEVICES)

            # Occasionally resend the previous event to simulate a duplicate.
            if previous_event is not None and random.random() < SIMULATION_CONFIG["duplicate_probability"]:
                telemetry = previous_event.copy()
                print("DUPLICATE:", json.dumps(telemetry))
            else:
                telemetry = generate_telemetry(device)
                previous_event = telemetry.copy()
                print(json.dumps(telemetry))

            write_event(telemetry)

            time.sleep(
                SIMULATION_CONFIG["event_interval_seconds"]
            )

    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()