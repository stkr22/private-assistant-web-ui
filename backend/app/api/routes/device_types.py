"""API routes for DeviceType management."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from private_assistant_commons.database.models import DeviceType
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.models_commons_api import (
    DeviceTypeCreate,
    DeviceTypePublic,
    DeviceTypesPublic,
    DeviceTypeUpdate,
)

router = APIRouter(prefix="/device-types", tags=["device-types"])


@router.get("/", response_model=DeviceTypesPublic)
async def read_device_types(session: SessionDep, _current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve device types with pagination."""
    count_statement = select(func.count()).select_from(DeviceType)
    result = await session.exec(count_statement)
    count = result.one()

    statement = select(DeviceType).offset(skip).limit(limit)
    result = await session.exec(statement)  # type: ignore[arg-type]
    device_types = result.all()

    return DeviceTypesPublic(data=list(device_types), count=count)  # type: ignore[arg-type]


@router.get("/{device_type_id}", response_model=DeviceTypePublic)
async def read_device_type(session: SessionDep, _current_user: CurrentUser, device_type_id: uuid.UUID) -> Any:
    """Get device type by ID."""
    device_type = await session.get(DeviceType, device_type_id)
    if not device_type:
        raise HTTPException(status_code=404, detail="Device type not found")
    return device_type


@router.post("/", response_model=DeviceTypePublic)
async def create_device_type(
    *, session: SessionDep, _current_user: CurrentUser, device_type_in: DeviceTypeCreate
) -> Any:
    """Create new device type."""
    device_type = DeviceType.model_validate(device_type_in)
    session.add(device_type)
    await session.commit()
    await session.refresh(device_type)
    return device_type


@router.put("/{device_type_id}", response_model=DeviceTypePublic)
async def update_device_type(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    device_type_id: uuid.UUID,
    device_type_in: DeviceTypeUpdate,
) -> Any:
    """Update a device type."""
    device_type = await session.get(DeviceType, device_type_id)
    if not device_type:
        raise HTTPException(status_code=404, detail="Device type not found")

    update_dict = device_type_in.model_dump(exclude_unset=True)
    device_type.sqlmodel_update(update_dict)
    session.add(device_type)
    await session.commit()
    await session.refresh(device_type)
    return device_type


@router.delete("/{device_type_id}")
async def delete_device_type(session: SessionDep, _current_user: CurrentUser, device_type_id: uuid.UUID) -> Message:
    """Delete a device type."""
    device_type = await session.get(DeviceType, device_type_id)
    if not device_type:
        raise HTTPException(status_code=404, detail="Device type not found")

    await session.delete(device_type)
    await session.commit()
    return Message(message="Device type deleted successfully")
