"""API models for private-assistant-commons entities.

These models define the API request/response schemas for commons entities
(Room, DeviceType, GlobalDevice) that are managed by the web-ui.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import SQLModel


# Room Models
class RoomBase(SQLModel):
    """Base model for Room."""

    name: str


class RoomCreate(RoomBase):
    """Model for creating a new room."""

    pass


class RoomUpdate(SQLModel):
    """Model for updating a room."""

    name: str | None = None


class RoomPublic(RoomBase):
    """Public API model for Room."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RoomsPublic(SQLModel):
    """Paginated response for rooms."""

    data: list[RoomPublic]
    count: int


# DeviceType Models
class DeviceTypeBase(SQLModel):
    """Base model for DeviceType."""

    name: str


class DeviceTypeCreate(DeviceTypeBase):
    """Model for creating a new device type."""

    pass


class DeviceTypeUpdate(SQLModel):
    """Model for updating a device type."""

    name: str | None = None


class DeviceTypePublic(DeviceTypeBase):
    """Public API model for DeviceType."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DeviceTypesPublic(SQLModel):
    """Paginated response for device types."""

    data: list[DeviceTypePublic]
    count: int


# GlobalDevice Models
class GlobalDeviceBase(SQLModel):
    """Base model for GlobalDevice."""

    name: str
    device_type_id: uuid.UUID
    room_id: uuid.UUID | None = None
    skill_id: uuid.UUID
    pattern: list[str] | None = None
    device_attributes: dict[str, Any] | None = None


class GlobalDeviceCreate(GlobalDeviceBase):
    """Model for creating a new global device."""

    pass


class GlobalDeviceUpdate(SQLModel):
    """Model for updating a global device."""

    name: str | None = None
    device_type_id: uuid.UUID | None = None
    room_id: uuid.UUID | None = None
    skill_id: uuid.UUID | None = None
    pattern: list[str] | None = None
    device_attributes: dict[str, Any] | None = None


class GlobalDevicePublic(GlobalDeviceBase):
    """Public API model for GlobalDevice."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class GlobalDevicesPublic(SQLModel):
    """Paginated response for global devices."""

    data: list[GlobalDevicePublic]
    count: int
