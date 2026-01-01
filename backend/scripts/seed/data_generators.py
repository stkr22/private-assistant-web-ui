"""Helper functions for generating realistic but fictional device data.

AIDEV-NOTE: All data here is fictional. Do not use real MQTT topics,
device IDs, or personally identifiable information.
"""

import random
import uuid
from typing import Any

# Fictional room names
ROOMS = ["bedroom", "living room", "kitchen", "bathroom", "hall", "office", "garage", "basement"]

# Device type to skill mapping
DEVICE_TYPE_SKILL_MAP: dict[str, str] = {
    "light": "switch",
    "switch": "switch",
    "plug": "switch",
    "bulb": "switch",
    "scene": "scene",
    "curtain": "curtain",
    "thermostat": "climate",
    "window_sensor": "iot-state",
    "picture_display": "picture-display",
    "spotify_device": "spotify",
}

# Device type definitions
DEVICE_TYPES = list(DEVICE_TYPE_SKILL_MAP.keys())

# Skill definitions
SKILLS = ["climate", "curtain", "switch", "scene", "iot-state", "picture-display", "spotify"]


def generate_mqtt_topic(room: str, device_type: str, device_name: str) -> str:
    """Generate a fictional MQTT topic.

    Pattern: fictional2mqtt/{room}/{device_type}/{device_name}/set
    """
    room_slug = room.lower().replace(" ", "_")
    return f"fictional2mqtt/{room_slug}/{device_type}/{device_name}/set"


def generate_switch_attributes(room: str, device_name: str) -> dict[str, Any]:
    """Generate attributes for switch-type devices (light, plug, bulb, switch)."""
    topic = generate_mqtt_topic(room, "switch", device_name)
    return {
        "topic": topic,
        "payload_on": '{"state": "ON"}',
        "payload_off": '{"state": "OFF"}',
    }


def generate_thermostat_attributes(room: str) -> dict[str, Any]:
    """Generate attributes for thermostat devices."""
    topic = generate_mqtt_topic(room, "thermostat", "main")
    return {
        "topic": topic,
        "payload_set_template": '{"occupied_heating_setpoint": {{ temperature }}}',
    }


def generate_curtain_attributes(room: str, device_name: str) -> dict[str, Any]:
    """Generate attributes for curtain devices."""
    topic = generate_mqtt_topic(room, "motor", device_name)
    return {
        "topic": topic,
        "payload_open": '{"state": "OPEN"}',
        "payload_close": '{"state": "CLOSE"}',
        "payload_set_template": '{"position": {{ position }}}',
    }


def generate_scene_attributes(scene_name: str, actions_count: int = 3) -> dict[str, Any]:
    """Generate attributes for scene devices."""
    actions = []
    for i in range(actions_count):
        actions.append(
            {
                "topic": f"fictional2mqtt/scene/{scene_name}/action_{i}/set",
                "payload": f'{{"state": "ON", "brightness": {random.randint(50, 254)}}}',
            }
        )
    return {"device_actions": actions}


def generate_picture_display_attributes() -> dict[str, Any]:
    """Generate attributes for picture display devices."""
    return {
        "display_width": random.choice([1600, 1920, 800]),
        "display_height": random.choice([1200, 1080, 600]),
        "orientation": random.choice(["landscape", "portrait"]),
        "model": f"fictional_display_{random.randint(1, 10)}",
    }


def generate_spotify_attributes() -> dict[str, Any]:
    """Generate attributes for Spotify devices."""
    # Generate a fictional Spotify device ID (40-char hex)
    spotify_id = uuid.uuid4().hex + uuid.uuid4().hex[:8]
    return {
        "spotify_id": spotify_id,
        "is_main": random.choice([True, False]),
        "default_volume": random.randint(30, 70),
    }


def generate_device_attributes(device_type: str, room: str | None, device_name: str) -> dict[str, Any] | None:
    """Generate appropriate attributes based on device type."""
    room_name = room or "common"

    # Map device types to their attribute generators
    generators: dict[str, dict[str, Any] | None] = {
        "light": generate_switch_attributes(room_name, device_name),
        "switch": generate_switch_attributes(room_name, device_name),
        "plug": generate_switch_attributes(room_name, device_name),
        "bulb": generate_switch_attributes(room_name, device_name),
        "thermostat": generate_thermostat_attributes(room_name),
        "curtain": generate_curtain_attributes(room_name, device_name),
        "scene": generate_scene_attributes(device_name),
        "picture_display": generate_picture_display_attributes(),
        "spotify_device": generate_spotify_attributes(),
    }
    return generators.get(device_type)  # Returns None for unknown types


# Fictional device names by type
DEVICE_NAMES: dict[str, list[str]] = {
    "light": ["ceiling", "wall", "worktop", "countertop", "desk"],
    "switch": ["main", "secondary", "wall_rocker"],
    "plug": ["chair_lamp", "desk_lamp", "shelf_light", "tripod", "cone"],
    "bulb": ["ceiling", "pendant", "floor"],
    "scene": ["daylight", "night", "movie", "reading", "party"],
    "curtain": ["curtains", "blinds", "shades"],
    "thermostat": ["main"],
    "window_sensor": ["window"],
    "picture_display": ["frame_alpha", "frame_beta", "kitchen_display"],
    "spotify_device": ["soundbar", "speaker", "echo"],
}


# Fictional image data
IMAGE_DATA: list[dict[str, Any]] = [
    {
        "source_name": "manual",
        "storage_path": "manual/mountain_landscape_001.jpg",
        "title": "Mountain Landscape",
        "description": "A serene mountain view at sunset.",
        "tags": "nature,mountain,sunset",
        "display_duration_seconds": 60,
        "priority": 5,
    },
    {
        "source_name": "manual",
        "storage_path": "manual/ocean_waves_002.jpg",
        "title": "Ocean Waves",
        "description": "Waves crashing on a rocky shore.",
        "tags": "nature,ocean,waves",
        "display_duration_seconds": 45,
        "priority": 7,
    },
    {
        "source_name": "manual",
        "storage_path": "manual/forest_path_003.jpg",
        "title": "Forest Path",
        "description": None,
        "tags": "nature,forest,path",
        "display_duration_seconds": 90,
        "priority": 3,
    },
]
