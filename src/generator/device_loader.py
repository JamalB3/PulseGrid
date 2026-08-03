from typing import Any

from core.config import BUILDINGS_FILE, DEVICE_TEMPLATES_FILE
from core.config_loader import load_json


def load_devices() -> list[dict[str, Any]]:
    """Create device definitions from buildings and room templates."""

    buildings = load_json(BUILDINGS_FILE)
    templates = load_json(DEVICE_TEMPLATES_FILE)

    devices: list[dict[str, Any]] = []
    device_number = 1

    for building in buildings:
        for floor in building["floors"]:
            for room in floor["rooms"]:
                room_type = room["room_type"]

                if room_type not in templates:
                    raise ValueError(
                        f"No device template exists for room type: "
                        f"{room_type}"
                    )

                template = templates[room_type]

                device = {
                    "device_id": f"sensor_{device_number:04d}",
                    "building_id": building["building_id"],
                    "building": building["name"],
                    "floor": floor["floor_number"],
                    "room_id": room["room_id"],
                    "room": room["name"],
                    "room_type": room_type,
                    **template,
                }

                devices.append(device)
                device_number += 1

    if not devices:
        raise ValueError(
            "No devices were generated from the configuration."
        )

    return devices