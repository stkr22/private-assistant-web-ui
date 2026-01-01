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
from typing import TypeVar

from private_assistant_commons.database.models import DeviceType, GlobalDevice, Room, Skill
from private_assistant_picture_display_skill.models.device import DeviceDisplayState
from private_assistant_picture_display_skill.models.image import Image
from sqlalchemy import delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_engine

from .factories import (
    DeviceDisplayStateFactory,
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


async def seed_database_async(clean: bool = False, dry_run: bool = False) -> None:
    """Main async seeding function.

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
            logger.info("Would seed: 8 rooms, 10 device types, 7 skills, ~40 devices, 3 images")
            return

        if clean:
            await clear_data(session)

        # Seed in dependency order
        # 1. Independent tables first
        rooms = await seed_rooms(session)
        device_types = await seed_device_types(session)
        skills = await seed_skills(session)

        # 2. Dependent tables
        devices = await seed_global_devices(session, rooms, device_types, skills)
        await seed_images(session)
        await seed_device_display_states(session, devices, device_types)

        # Final commit
        await session.commit()

        # Report final counts
        final_counts = await check_existing_data(session)
        logger.info(f"Final data counts: {final_counts}")
        logger.info("Database seeding completed successfully!")


def seed_database(clean: bool = False, dry_run: bool = False) -> None:
    """Synchronous wrapper for async seeding function."""
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
