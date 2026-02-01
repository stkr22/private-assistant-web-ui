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


# IntentPatternKeyword Models
class IntentPatternKeywordBase(SQLModel):
    """Base model for IntentPatternKeyword."""

    keyword: str
    keyword_type: str = "primary"  # primary or negative
    is_regex: bool = False
    weight: float = 1.0


class IntentPatternKeywordCreate(IntentPatternKeywordBase):
    """Model for creating a new keyword (nested in IntentPattern)."""


class IntentPatternKeywordUpdate(SQLModel):
    """Model for updating a keyword."""

    keyword: str | None = None
    keyword_type: str | None = None
    is_regex: bool | None = None
    weight: float | None = None


class IntentPatternKeywordPublic(IntentPatternKeywordBase):
    """Public API model for IntentPatternKeyword."""

    id: uuid.UUID
    pattern_id: uuid.UUID
    created_at: datetime


# IntentPattern Models
class IntentPatternBase(SQLModel):
    """Base model for IntentPattern."""

    intent_type: str
    enabled: bool = True
    priority: int = 0
    description: str | None = None


class IntentPatternCreate(IntentPatternBase):
    """Model for creating a new intent pattern with keywords."""

    keywords: list[IntentPatternKeywordCreate] = []


class IntentPatternUpdate(SQLModel):
    """Model for updating an intent pattern."""

    intent_type: str | None = None
    enabled: bool | None = None
    priority: int | None = None
    description: str | None = None
    keywords: list[IntentPatternKeywordCreate] | None = None  # Replace all keywords


class IntentPatternPublic(IntentPatternBase):
    """Public API model for IntentPattern with nested keywords."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    keywords: list[IntentPatternKeywordPublic]


class IntentPatternsPublic(SQLModel):
    """Paginated response for intent patterns."""

    data: list[IntentPatternPublic]
    count: int


# SkillIntent Models
class SkillIntentBase(SQLModel):
    """Base model for SkillIntent."""

    skill_id: uuid.UUID
    intent_pattern_id: uuid.UUID


class SkillIntentCreate(SkillIntentBase):
    """Model for creating a new skill-intent mapping."""


class SkillIntentPublic(SkillIntentBase):
    """Public API model for SkillIntent."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SkillIntentsPublic(SQLModel):
    """Paginated response for skill-intents."""

    data: list[SkillIntentPublic]
    count: int
