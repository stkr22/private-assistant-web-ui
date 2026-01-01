"""API schema models for picture display endpoints.

These Pydantic models define the API contract for picture display operations.
They are separate from the database models to allow API-specific validation
and response shaping.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ImagePublic(BaseModel):
    """API response model for Image."""

    id: UUID
    source_name: str
    storage_path: str
    title: str | None
    description: str | None
    author: str | None
    source_url: str | None
    tags: str | None
    display_duration_seconds: int
    priority: int
    original_width: int | None
    original_height: int | None
    last_displayed_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ImageCreate(BaseModel):
    """API request model for creating images via upload."""

    source_name: str = Field(max_length=255)
    storage_path: str = Field(max_length=512)
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    tags: str | None = Field(default=None, max_length=500)
    display_duration_seconds: int = Field(default=3600, ge=5, le=86400)
    priority: int = Field(default=0, ge=0, le=100)


class ImageUpdate(BaseModel):
    """API request model for updating images."""

    title: str | None = None
    description: str | None = None
    tags: str | None = None
    display_duration_seconds: int | None = Field(default=None, ge=5, le=86400)
    priority: int | None = Field(default=None, ge=0, le=100)


class ImagesPublic(BaseModel):
    """Paginated response for images."""

    data: list[ImagePublic]
    count: int
