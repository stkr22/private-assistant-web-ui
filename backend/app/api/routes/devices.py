"""API routes for GlobalDevice management with MQTT notifications."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from private_assistant_commons.database.models import DeviceType, GlobalDevice, Room, Skill
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.core.mqtt import publish_device_update
from app.models import Message
from app.models_commons_api import (
    GlobalDeviceCreate,
    GlobalDevicePublic,
    GlobalDevicesPublic,
    GlobalDeviceUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/", response_model=GlobalDevicesPublic)
async def read_devices(session: SessionDep, _current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve global devices with pagination."""
    count_statement = select(func.count()).select_from(GlobalDevice)
    result = await session.exec(count_statement)
    count = result.one()

    statement = select(GlobalDevice).offset(skip).limit(limit)
    result = await session.exec(statement)  # type: ignore[arg-type]
    devices = result.all()

    return GlobalDevicesPublic(data=list(devices), count=count)  # type: ignore[arg-type]


@router.get("/{device_id}", response_model=GlobalDevicePublic)
async def read_device(session: SessionDep, _current_user: CurrentUser, device_id: uuid.UUID) -> Any:
    """Get device by ID."""
    device = await session.get(GlobalDevice, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/", response_model=GlobalDevicePublic)
async def create_device(*, session: SessionDep, _current_user: CurrentUser, device_in: GlobalDeviceCreate) -> Any:
    """Create new global device."""
    # Validate device_type_id exists
    device_type = await session.get(DeviceType, device_in.device_type_id)
    if not device_type:
        raise HTTPException(status_code=400, detail="Device type not found")

    # Validate skill_id exists
    skill = await session.get(Skill, device_in.skill_id)
    if not skill:
        raise HTTPException(status_code=400, detail="Skill not found")

    # Validate room_id if provided
    if device_in.room_id:
        room = await session.get(Room, device_in.room_id)
        if not room:
            raise HTTPException(status_code=400, detail="Room not found")

    # Create device
    device = GlobalDevice.model_validate(device_in)
    session.add(device)
    await session.commit()
    await session.refresh(device)

    # Publish MQTT notification
    try:
        await publish_device_update(str(device.id), "created")
    except Exception as e:
        logger.error(f"Failed to publish MQTT event for device creation: {e}")
        # Don't fail the request if MQTT fails

    return device


@router.put("/{device_id}", response_model=GlobalDevicePublic)
async def update_device(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    device_id: uuid.UUID,
    device_in: GlobalDeviceUpdate,
) -> Any:
    """Update a global device."""
    device = await session.get(GlobalDevice, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Extract update data
    update_dict = device_in.model_dump(exclude_unset=True)

    # Validate device_type_id if being updated
    if "device_type_id" in update_dict:
        device_type = await session.get(DeviceType, update_dict["device_type_id"])
        if not device_type:
            raise HTTPException(status_code=400, detail="Device type not found")

    # Validate skill_id if being updated
    if "skill_id" in update_dict:
        skill = await session.get(Skill, update_dict["skill_id"])
        if not skill:
            raise HTTPException(status_code=400, detail="Skill not found")

    # Validate room_id if being updated
    if "room_id" in update_dict and update_dict["room_id"] is not None:
        room = await session.get(Room, update_dict["room_id"])
        if not room:
            raise HTTPException(status_code=400, detail="Room not found")

    # Update device
    device.sqlmodel_update(update_dict)
    session.add(device)
    await session.commit()
    await session.refresh(device)

    # Publish MQTT notification
    try:
        await publish_device_update(str(device.id), "updated")
    except Exception as e:
        logger.error(f"Failed to publish MQTT event for device update: {e}")
        # Don't fail the request if MQTT fails

    return device


@router.delete("/{device_id}")
async def delete_device(session: SessionDep, _current_user: CurrentUser, device_id: uuid.UUID) -> Message:
    """Delete a global device."""
    device = await session.get(GlobalDevice, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Store device_id as string before deletion
    device_id_str = str(device.id)

    await session.delete(device)
    await session.commit()

    # Publish MQTT notification
    try:
        await publish_device_update(device_id_str, "deleted")
    except Exception as e:
        logger.error(f"Failed to publish MQTT event for device deletion: {e}")
        # Don't fail the request if MQTT fails

    return Message(message="Device deleted successfully")
