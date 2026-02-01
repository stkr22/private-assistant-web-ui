#!/usr/bin/env python3
"""Database seeding script using Factory Boy.

AIDEV-NOTE: This script uses async SQLAlchemy for database operations.
Run with: uv run python -m scripts.seed.seed_database

Usage:
    uv run python -m scripts.seed.seed_database           # Seed with defaults
    uv run python -m scripts.seed.seed_database --clean   # Clear existing data first
    uv run python -m scripts.seed.seed_database --dry-run # Preview without changes
"""

import argparse
import asyncio
import contextlib
import logging
import sys
from typing import TypedDict, TypeVar

from private_assistant_commons.database.device_models import DeviceType, GlobalDevice, Room
from private_assistant_commons.database.intent_pattern_models import IntentPattern, IntentPatternKeyword
from private_assistant_commons.database.skill_models import Skill, SkillIntent
from private_assistant_picture_display_skill.models.device import DeviceDisplayState
from private_assistant_picture_display_skill.models.image import Image
from sqlalchemy import delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_engine

from .factories import (
    DeviceDisplayStateFactory,
    IntentPatternFactory,
    IntentPatternKeywordFactory,
    SkillIntentFactory,
    build_all_device_types,
    build_all_images,
    build_all_rooms,
    build_all_skills,
    build_devices_for_room,
    build_roomless_devices,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

T = TypeVar("T")


async def get_or_create(session: AsyncSession, model: type[T], name: str, instance: T) -> T:
    """Get existing record by name or insert new one."""
    statement = select(model).where(model.name == name)  # type: ignore[attr-defined]
    result = await session.exec(statement)
    existing = result.first()
    if existing:
        logger.debug(f"{model.__name__} '{name}' already exists")
        return existing

    session.add(instance)
    await session.flush()
    logger.debug(f"Created {model.__name__} '{name}'")
    return instance


async def check_existing_data(session: AsyncSession) -> dict[str, int]:
    """Check for existing data in all tables."""
    counts: dict[str, int] = {}
    for model, name in [
        (Room, "rooms"),
        (DeviceType, "device_types"),
        (Skill, "skills"),
        (GlobalDevice, "global_devices"),
        (Image, "images"),
        (DeviceDisplayState, "device_display_states"),
        (IntentPattern, "intent_patterns"),
        (IntentPatternKeyword, "intent_pattern_keywords"),
        (SkillIntent, "skill_intents"),
    ]:
        try:
            result = await session.exec(select(model))  # type: ignore[arg-type, var-annotated]
            counts[name] = len(result.all())
        except Exception:
            # Table might not exist yet
            counts[name] = 0
    return counts


async def clear_data(session: AsyncSession) -> None:
    """Clear all seeded data in reverse dependency order.

    AIDEV-NOTE: Uses DELETE in dependency order to avoid FK violations.
    """
    logger.info("Clearing existing data...")

    # Delete in reverse dependency order
    with contextlib.suppress(Exception):
        await session.exec(delete(DeviceDisplayState))  # type: ignore[call-overload]
    with contextlib.suppress(Exception):
        await session.exec(delete(Image))  # type: ignore[call-overload]
    with contextlib.suppress(Exception):
        await session.exec(delete(SkillIntent))  # type: ignore[call-overload]
    with contextlib.suppress(Exception):
        await session.exec(delete(IntentPatternKeyword))  # type: ignore[call-overload]
    with contextlib.suppress(Exception):
        await session.exec(delete(IntentPattern))  # type: ignore[call-overload]
    await session.exec(delete(GlobalDevice))  # type: ignore[call-overload]
    # Note: Room, DeviceType, Skill are from commons - be careful about deleting

    await session.commit()
    logger.info("Data cleared successfully (kept base entity tables)")


async def seed_rooms(session: AsyncSession) -> dict[str, Room]:
    """Seed Room table and return name->instance mapping."""
    logger.info("Seeding rooms...")
    rooms = {}
    built_rooms = build_all_rooms()

    for room in built_rooms:
        persisted = await get_or_create(session, Room, room.name, room)
        rooms[room.name] = persisted

    logger.info(f"Seeded {len(rooms)} rooms")
    return rooms


async def seed_device_types(session: AsyncSession) -> dict[str, DeviceType]:
    """Seed DeviceType table and return name->instance mapping."""
    logger.info("Seeding device types...")
    device_types = {}
    built_types = build_all_device_types()

    for dt in built_types:
        persisted = await get_or_create(session, DeviceType, dt.name, dt)
        device_types[dt.name] = persisted

    logger.info(f"Seeded {len(device_types)} device types")
    return device_types


async def seed_skills(session: AsyncSession) -> dict[str, Skill]:
    """Seed Skill table and return name->instance mapping."""
    logger.info("Seeding skills...")
    skills = {}
    built_skills = build_all_skills()

    for skill in built_skills:
        persisted = await get_or_create(session, Skill, skill.name, skill)
        skills[skill.name] = persisted

    logger.info(f"Seeded {len(skills)} skills")
    return skills


async def seed_global_devices(
    session: AsyncSession,
    rooms: dict[str, Room],
    device_types: dict[str, DeviceType],
    skills: dict[str, Skill],
) -> list[GlobalDevice]:
    """Seed GlobalDevice table with realistic device configurations."""
    logger.info("Seeding global devices...")
    devices = []

    # Build devices for each room
    for room in rooms.values():
        room_devices = build_devices_for_room(room, device_types, skills)
        for device in room_devices:
            # Check if device already exists (by name + room + device_type)
            statement = select(GlobalDevice).where(
                GlobalDevice.name == device.name,
                GlobalDevice.device_type_id == device.device_type_id,
                GlobalDevice.room_id == device.room_id,
            )
            result = await session.exec(statement)
            existing = result.first()
            if existing:
                devices.append(existing)
                continue

            session.add(device)
            await session.flush()
            devices.append(device)

    # Build roomless devices (scenes, spotify)
    roomless_devices = build_roomless_devices(device_types, skills)
    for device in roomless_devices:
        statement = select(GlobalDevice).where(
            GlobalDevice.name == device.name,
            GlobalDevice.device_type_id == device.device_type_id,
            GlobalDevice.room_id == None,  # noqa: E711 - SQLAlchemy requires == for IS NULL
        )
        result = await session.exec(statement)
        existing = result.first()
        if existing:
            devices.append(existing)
            continue

        session.add(device)
        await session.flush()
        devices.append(device)

    logger.info(f"Seeded {len(devices)} global devices")
    return devices


async def seed_images(session: AsyncSession) -> list[Image]:
    """Seed Image table with fictional images."""
    logger.info("Seeding images...")
    images = []
    built_images = build_all_images()

    for image in built_images:
        # Check if image already exists by storage_path
        statement = select(Image).where(Image.storage_path == image.storage_path)
        result = await session.exec(statement)
        existing = result.first()

        if existing:
            images.append(existing)
            continue

        session.add(image)
        await session.flush()
        images.append(image)

    logger.info(f"Seeded {len(images)} images")
    return images


async def seed_device_display_states(
    session: AsyncSession,
    devices: list[GlobalDevice],
    device_types: dict[str, DeviceType],
) -> list[DeviceDisplayState]:
    """Seed DeviceDisplayState for picture_display type devices."""
    logger.info("Seeding device display states...")
    display_states: list[DeviceDisplayState] = []

    picture_display_type = device_types.get("picture_display")
    if not picture_display_type:
        logger.warning("No picture_display device type found, skipping display states")
        return display_states

    for device in devices:
        if device.device_type_id != picture_display_type.id:
            continue

        # Check if display state already exists
        statement = select(DeviceDisplayState).where(DeviceDisplayState.global_device_id == device.id)
        result = await session.exec(statement)
        existing = result.first()

        if existing:
            display_states.append(existing)
            continue

        display_state = DeviceDisplayStateFactory.build(global_device_id=device.id)
        session.add(display_state)
        await session.flush()
        display_states.append(display_state)

    logger.info(f"Seeded {len(display_states)} device display states")
    return display_states


class KeywordConfig(TypedDict):
    """Type definition for keyword configuration."""

    keyword: str
    keyword_type: str
    weight: float


class IntentConfig(TypedDict):
    """Type definition for intent pattern configuration."""

    intent_type: str
    description: str
    priority: int
    keywords: list[KeywordConfig]


async def seed_intent_patterns(session: AsyncSession) -> dict[str, IntentPattern]:
    """Seed IntentPattern records with realistic intent types and keywords.

    Returns:
        Dictionary mapping intent_type to IntentPattern for easy linking.

    """
    logger.info("Seeding intent patterns...")

    # Define intent patterns matching IntentType enum from private-assistant-commons
    intent_configs: list[IntentConfig] = [
        # Device Control
        {
            "intent_type": "device.on",
            "description": "Turn on a device",
            "priority": 100,
            "keywords": [
                {"keyword": "turn on", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "switch on", "keyword_type": "primary", "weight": 0.9},
                {"keyword": "activate", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        {
            "intent_type": "device.off",
            "description": "Turn off a device",
            "priority": 100,
            "keywords": [
                {"keyword": "turn off", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "switch off", "keyword_type": "primary", "weight": 0.9},
                {"keyword": "deactivate", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        {
            "intent_type": "device.set",
            "description": "Set device to a specific state or value",
            "priority": 95,
            "keywords": [
                {"keyword": "set", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "adjust", "keyword_type": "primary", "weight": 0.9},
                {"keyword": "change", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        {
            "intent_type": "device.open",
            "description": "Open a device (blinds, curtains, doors, etc.)",
            "priority": 95,
            "keywords": [
                {"keyword": "open", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "raise", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        {
            "intent_type": "device.close",
            "description": "Close a device (blinds, curtains, doors, etc.)",
            "priority": 95,
            "keywords": [
                {"keyword": "close", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "lower", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        # Media Control
        {
            "intent_type": "media.play",
            "description": "Play media content",
            "priority": 90,
            "keywords": [
                {"keyword": "play", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "start", "keyword_type": "primary", "weight": 0.8},
                {"keyword": "resume", "keyword_type": "primary", "weight": 0.7},
            ],
        },
        {
            "intent_type": "media.stop",
            "description": "Stop media playback",
            "priority": 90,
            "keywords": [
                {"keyword": "stop", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "pause", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        {
            "intent_type": "media.next",
            "description": "Skip to next media track",
            "priority": 85,
            "keywords": [
                {"keyword": "next", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "skip", "keyword_type": "primary", "weight": 0.9},
            ],
        },
        {
            "intent_type": "media.volume_up",
            "description": "Increase media volume",
            "priority": 85,
            "keywords": [
                {"keyword": "volume up", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "louder", "keyword_type": "primary", "weight": 0.9},
                {"keyword": "increase volume", "keyword_type": "primary", "weight": 0.9},
            ],
        },
        {
            "intent_type": "media.volume_down",
            "description": "Decrease media volume",
            "priority": 85,
            "keywords": [
                {"keyword": "volume down", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "quieter", "keyword_type": "primary", "weight": 0.9},
                {"keyword": "decrease volume", "keyword_type": "primary", "weight": 0.9},
            ],
        },
        {
            "intent_type": "media.volume_set",
            "description": "Set media volume to specific level",
            "priority": 85,
            "keywords": [
                {"keyword": "set volume", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "volume", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        # Queries
        {
            "intent_type": "device.query",
            "description": "Query device status or state",
            "priority": 80,
            "keywords": [
                {"keyword": "what is", "keyword_type": "primary", "weight": 0.9},
                {"keyword": "how is", "keyword_type": "primary", "weight": 0.9},
                {"keyword": "is", "keyword_type": "primary", "weight": 0.7},
            ],
        },
        {
            "intent_type": "media.query",
            "description": "Query media information",
            "priority": 80,
            "keywords": [
                {"keyword": "what's playing", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "what song", "keyword_type": "primary", "weight": 0.9},
            ],
        },
        {
            "intent_type": "data.query",
            "description": "Query general data or information",
            "priority": 75,
            "keywords": [
                {"keyword": "what", "keyword_type": "primary", "weight": 0.8},
                {"keyword": "tell me", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        # Scene/Automation
        {
            "intent_type": "scene.apply",
            "description": "Apply a scene or automation",
            "priority": 85,
            "keywords": [
                {"keyword": "activate scene", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "scene", "keyword_type": "primary", "weight": 0.8},
            ],
        },
        # Time/Scheduling
        {
            "intent_type": "schedule.set",
            "description": "Set a schedule or timer",
            "priority": 80,
            "keywords": [
                {"keyword": "schedule", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "set timer", "keyword_type": "primary", "weight": 1.0},
            ],
        },
        {
            "intent_type": "schedule.cancel",
            "description": "Cancel a schedule or timer",
            "priority": 80,
            "keywords": [
                {"keyword": "cancel schedule", "keyword_type": "primary", "weight": 1.0},
                {"keyword": "cancel timer", "keyword_type": "primary", "weight": 1.0},
            ],
        },
    ]

    patterns: dict[str, IntentPattern] = {}

    for config in intent_configs:
        # Check if pattern already exists
        statement = select(IntentPattern).where(IntentPattern.intent_type == config["intent_type"])  # type: ignore[attr-defined]
        result = await session.exec(statement)  # type: ignore[arg-type]
        existing = result.first()

        if existing:
            patterns[config["intent_type"]] = existing
            logger.debug(f"IntentPattern '{config['intent_type']}' already exists")
            continue

        # Create new pattern
        pattern = IntentPatternFactory.build(
            intent_type=config["intent_type"],
            description=config["description"],
            priority=config["priority"],
            enabled=True,
        )
        session.add(pattern)
        await session.flush()

        # Create keywords for this pattern
        for kw_config in config["keywords"]:
            keyword = IntentPatternKeywordFactory.build(
                pattern_id=pattern.id,
                keyword=kw_config["keyword"],
                keyword_type=kw_config["keyword_type"],
                weight=kw_config["weight"],
                is_regex=False,
            )
            session.add(keyword)

        await session.flush()
        patterns[config["intent_type"]] = pattern
        logger.debug(f"Created IntentPattern '{config['intent_type']}' with {len(config['keywords'])} keywords")

    logger.info(f"Seeded {len(patterns)} intent patterns")
    return patterns


async def seed_skill_intents(
    session: AsyncSession,
    skills: dict[str, Skill],
    intent_patterns: dict[str, IntentPattern],
) -> list[SkillIntent]:
    """Link skills to their supported intent patterns.

    Args:
        session: Database session
        skills: Dictionary of skills by name
        intent_patterns: Dictionary of intent patterns by intent_type

    """
    logger.info("Seeding skill intents...")

    # Define which skills support which intents (using valid IntentType values)
    skill_intent_mapping = {
        "switch": ["device.on", "device.off", "device.query"],
        "curtain": ["device.open", "device.close", "device.query"],
        "spotify": [
            "media.play",
            "media.stop",
            "media.next",
            "media.volume_up",
            "media.volume_down",
            "media.volume_set",
            "media.query",
        ],
        "climate": ["device.set", "device.on", "device.off", "device.query"],
        "picture-display": ["device.query"],
        "iot-state": ["device.query", "data.query"],
        "scene": ["scene.apply", "device.query"],
    }

    skill_intents: list[SkillIntent] = []

    for skill_name, intent_types in skill_intent_mapping.items():
        skill = skills.get(skill_name)
        if not skill:
            logger.warning(f"Skill '{skill_name}' not found, skipping intent mapping")
            continue

        for intent_type in intent_types:
            pattern = intent_patterns.get(intent_type)
            if not pattern:
                logger.warning(f"IntentPattern '{intent_type}' not found, skipping")
                continue

            # Check if mapping already exists
            statement = select(SkillIntent).where(
                SkillIntent.skill_id == skill.id, SkillIntent.intent_pattern_id == pattern.id  # type: ignore[attr-defined]
            )
            result = await session.exec(statement)  # type: ignore[arg-type]
            existing = result.first()

            if existing:
                skill_intents.append(existing)
                continue

            # Create new mapping
            skill_intent = SkillIntentFactory.build(
                skill_id=skill.id,
                intent_pattern_id=pattern.id,
            )
            session.add(skill_intent)
            await session.flush()
            skill_intents.append(skill_intent)
            logger.debug(f"Linked skill '{skill_name}' to intent '{intent_type}'")

    logger.info(f"Seeded {len(skill_intents)} skill intent mappings")
    return skill_intents


async def seed_database_async(clean: bool = False, dry_run: bool = False) -> None:
    """Seed the database with initial data.

    Args:
        clean: If True, clear existing data before seeding
        dry_run: If True, preview changes without committing

    """
    logger.info("Starting database seeding...")

    async with AsyncSession(get_engine()) as session:
        # Check existing data
        existing_counts = await check_existing_data(session)
        logger.info(f"Existing data: {existing_counts}")

        if dry_run:
            logger.info("DRY RUN - No changes will be made")
            logger.info(
                "Would seed: 8 rooms, 10 device types, 7 skills, ~40 devices, "
                "3 images, 17 intent patterns, ~22 skill intents"
            )
            return

        if clean:
            await clear_data(session)

        # Seed in dependency order
        # 1. Independent tables first
        rooms = await seed_rooms(session)
        device_types = await seed_device_types(session)
        skills = await seed_skills(session)
        intent_patterns = await seed_intent_patterns(session)

        # 2. Dependent tables
        devices = await seed_global_devices(session, rooms, device_types, skills)
        await seed_images(session)
        await seed_device_display_states(session, devices, device_types)
        await seed_skill_intents(session, skills, intent_patterns)

        # Final commit
        await session.commit()

        # Report final counts
        final_counts = await check_existing_data(session)
        logger.info(f"Final data counts: {final_counts}")
        logger.info("Database seeding completed successfully!")


def seed_database(clean: bool = False, dry_run: bool = False) -> None:
    """Run async seeding function synchronously."""
    asyncio.run(seed_database_async(clean=clean, dry_run=dry_run))


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Seed the database with test data")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clear existing data before seeding",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them",
    )

    args = parser.parse_args()

    try:
        seed_database(clean=args.clean, dry_run=args.dry_run)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
