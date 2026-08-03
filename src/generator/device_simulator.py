import json
import random
import time
from datetime import datetime, timezone
from typing import Any
from generator.file_writer import write_event
from uuid import uuid4


DEVICES = [
    {
        "device_id": "sensor_001",
        "location": "conference_room",
        "temperature_range": (70.0, 75.0),
        "humidity_range": (40.0, 60.0),
        "energy_range": (1.0, 4.5),
        "air_quality_range": (20, 70),
        "occupancy_range": (0, 25),
    },
    {
        "device_id": "sensor_002",
        "location": "server_room",
        "temperature_range": (68.0, 78.0),
        "humidity_range": (35.0, 45.0),
        "energy_range": (3.0, 8.0),
        "air_quality_range": (15, 50),
        "occupancy_range": (0, 2),
    },
    {
        "device_id": "sensor_003",
        "location": "lobby",
        "temperature_range": (70.0, 77.0),
        "humidity_range": (40.0, 65.0),
        "energy_range": (1.5, 5.5),
        "air_quality_range": (20, 80),
        "occupancy_range": (0, 50),
    },
    {
        "device_id": "sensor_004",
        "location": "office_1",
        "temperature_range": (69.0, 76.0),
        "humidity_range": (38.0, 58.0),
        "energy_range": (0.5, 3.0),
        "air_quality_range": (20, 65),
        "occupancy_range": (0, 6),
    },
    {
        "device_id": "sensor_005",
        "location": "office_2",
        "temperature_range": (69.0, 76.0),
        "humidity_range": (38.0, 58.0),
        "energy_range": (0.5, 3.0),
        "air_quality_range": (20, 65),
        "occupancy_range": (0, 6),
    },
]


def random_decimal(value_range: tuple[float, float]) -> float:
    """Generate a rounded decimal within the provided range."""

    minimum, maximum = value_range
    return round(random.uniform(minimum, maximum), 2)


def generate_telemetry(device: dict[str, Any]) -> dict[str, Any]:
    """Generate one realistic telemetry event for a simulated device."""

    event = {
        "event_id": str(uuid4()),
        "device_id": device["device_id"],
        "location": device["location"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": random_decimal(device["temperature_range"]),
        "humidity": random_decimal(device["humidity_range"]),
        "energy_usage": random_decimal(device["energy_range"]),
        "air_quality": random.randint(*device["air_quality_range"]),
        "occupancy": random.randint(*device["occupancy_range"]),
    }

    # Introduce occasional data-quality problems.
    anomaly_roll = random.random()

    if anomaly_roll < 0.02:
        event["temperature"] = 999.0
    elif anomaly_roll < 0.04:
        event["humidity"] = None
    elif anomaly_roll < 0.06:
        event["device_id"] = None
    elif anomaly_roll < 0.08:
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
            if previous_event is not None and random.random() < 0.05:
                telemetry = previous_event.copy()
                print("DUPLICATE:", json.dumps(telemetry))
            else:
                telemetry = generate_telemetry(device)
                previous_event = telemetry.copy()
                print(json.dumps(telemetry))

            write_event(telemetry)

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()