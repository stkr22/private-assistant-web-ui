"""Factory Boy factories for database seeding.

AIDEV-NOTE: These factories use Factory.build() to create model instances
without database persistence. The seed script handles async insertion.
"""

import uuid
from datetime import datetime
from typing import Any

import factory
from private_assistant_commons.database.models import DeviceType, GlobalDevice, Room, Skill
from private_assistant_picture_display_skill.models.device import DeviceDisplayState
from private_assistant_picture_display_skill.models.image import Image

from .data_generators import (
    DEVICE_NAMES,
    DEVICE_TYPE_SKILL_MAP,
    DEVICE_TYPES,
    IMAGE_DATA,
    ROOMS,
    SKILLS,
    generate_device_attributes,
)


def utcnow() -> datetime:
    """Return current UTC time as naive datetime (no timezone info).

    AIDEV-NOTE: Database uses TIMESTAMP WITHOUT TIME ZONE, so we must
    provide naive datetimes. Using datetime.utcnow() pattern.
    """
    return datetime.utcnow()


class RoomFactory(factory.Factory):
    """Factory for Room model."""

    class Meta:
        model = Room

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Iterator(ROOMS)
    created_at = factory.LazyFunction(utcnow)
    updated_at = factory.LazyFunction(utcnow)


class DeviceTypeFactory(factory.Factory):
    """Factory for DeviceType model."""

    class Meta:
        model = DeviceType

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Iterator(DEVICE_TYPES)
    created_at = factory.LazyFunction(utcnow)
    updated_at = factory.LazyFunction(utcnow)


class SkillFactory(factory.Factory):
    """Factory for Skill model."""

    class Meta:
        model = Skill

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Iterator(SKILLS)
    created_at = factory.LazyFunction(utcnow)
    updated_at = factory.LazyFunction(utcnow)


class GlobalDeviceFactory(factory.Factory):
    """Factory for GlobalDevice model.

    AIDEV-NOTE: This factory requires device_type_id, room_id, and skill_id
    to be passed explicitly when building devices with relationships.
    """

    class Meta:
        model = GlobalDevice

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("word")
    pattern = factory.LazyAttribute(lambda obj: [obj.name.lower()])
    device_type_id = factory.LazyFunction(uuid.uuid4)
    room_id = None
    skill_id = factory.LazyFunction(uuid.uuid4)
    device_attributes: dict[str, Any] | None = None
    created_at = factory.LazyFunction(utcnow)
    updated_at = factory.LazyFunction(utcnow)

    @classmethod
    def build_with_attributes(
        cls,
        device_type_name: str,
        room_name: str | None,
        **kwargs: Any,
    ) -> GlobalDevice:
        """Build a device with appropriate attributes based on device type."""
        name = kwargs.get("name", "device")
        attributes = generate_device_attributes(device_type_name, room_name, name)
        result: GlobalDevice = cls.build(device_attributes=attributes, **kwargs)
        return result


class ImageFactory(factory.Factory):
    """Factory for Image model from skill package."""

    class Meta:
        model = Image

    id = factory.LazyFunction(uuid.uuid4)
    source_name = factory.Faker("word")
    storage_path = "manual upload"
    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph", nb_sentences=2)
    tags = factory.LazyFunction(lambda: "nature,landscape,scenic")
    display_duration_seconds = factory.Faker("random_int", min=1800, max=7200)
    priority = factory.Faker("random_int", min=0, max=10)
    last_displayed_at = None
    created_at = factory.LazyFunction(utcnow)
    updated_at = factory.LazyFunction(utcnow)


class DeviceDisplayStateFactory(factory.Factory):
    """Factory for DeviceDisplayState model from skill package.

    AIDEV-NOTE: Requires global_device_id to be passed explicitly.
    """

    class Meta:
        model = DeviceDisplayState

    global_device_id = factory.LazyFunction(uuid.uuid4)
    is_online = True
    current_image_id = None
    displayed_since = None
    scheduled_next_at = factory.LazyFunction(utcnow)


# Pre-built data collections for convenience
def build_all_rooms() -> list[Room]:
    """Build all predefined rooms."""
    return [RoomFactory.build(name=name) for name in ROOMS]


def build_all_device_types() -> list[DeviceType]:
    """Build all predefined device types."""
    return [DeviceTypeFactory.build(name=name) for name in DEVICE_TYPES]


def build_all_skills() -> list[Skill]:
    """Build all predefined skills."""
    return [SkillFactory.build(name=name) for name in SKILLS]


def build_all_images() -> list[Image]:
    """Build all predefined images."""
    return [ImageFactory.build(**img_data) for img_data in IMAGE_DATA]


def build_devices_for_room(
    room: Room,
    device_types: dict[str, DeviceType],
    skills: dict[str, Skill],
) -> list[GlobalDevice]:
    """Build devices for a specific room."""
    devices = []

    for dt_name, device_names in DEVICE_NAMES.items():
        # Skip room-independent devices
        if dt_name in ("scene", "spotify_device"):
            continue

        device_type = device_types.get(dt_name)
        skill_name = DEVICE_TYPE_SKILL_MAP.get(dt_name, "switch")
        skill = skills.get(skill_name)

        if not device_type or not skill:
            continue

        # Create one device of each name for this room
        for device_name in device_names[:2]:  # Limit to 2 per type per room
            device = GlobalDeviceFactory.build_with_attributes(
                device_type_name=dt_name,
                room_name=room.name,
                name=device_name,
                device_type_id=device_type.id,
                room_id=room.id,
                skill_id=skill.id,
                pattern=[device_name.lower()],
            )
            devices.append(device)

    return devices


def build_roomless_devices(
    device_types: dict[str, DeviceType],
    skills: dict[str, Skill],
) -> list[GlobalDevice]:
    """Build devices that don't belong to any room (scenes, spotify)."""
    devices = []

    for dt_name in ("scene", "spotify_device"):
        device_type = device_types.get(dt_name)
        skill_name = DEVICE_TYPE_SKILL_MAP.get(dt_name, "switch")
        skill = skills.get(skill_name)

        if not device_type or not skill:
            continue

        device_names = DEVICE_NAMES.get(dt_name, [])
        for device_name in device_names:
            device = GlobalDeviceFactory.build_with_attributes(
                device_type_name=dt_name,
                room_name=None,
                name=device_name,
                device_type_id=device_type.id,
                room_id=None,
                skill_id=skill.id,
                pattern=[device_name.lower()],
            )
            devices.append(device)

    return devices
