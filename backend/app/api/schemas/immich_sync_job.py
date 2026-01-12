"""API schema models for Immich sync job endpoints.

These Pydantic models define the API contract for Immich sync job operations.
They mirror the database model from the picture display skill package but
provide API-specific validation and response shaping.
"""

from datetime import datetime
from uuid import UUID

from private_assistant_picture_display_skill.models.immich_sync_job import SyncStrategy
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ImmichSyncJobBase(BaseModel):
    """Base schema with shared fields."""

    name: str = Field(min_length=1, max_length=255, description="Unique job name")
    target_device_id: UUID = Field(description="Device this job syncs for")
    strategy: SyncStrategy = Field(
        default=SyncStrategy.RANDOM,
        description="Selection strategy: RANDOM or SMART",
    )
    query: str | None = Field(
        default=None,
        max_length=500,
        description="Semantic search query for SMART strategy",
    )
    count: int = Field(default=10, ge=1, le=1000, description="Images to sync per run")
    random_pick: bool = Field(
        default=False,
        description="Randomly sample from smart search results",
    )
    overfetch_multiplier: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Multiplier for overfetching when client-side filters active",
    )
    min_color_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum color compatibility score (0 to disable)",
    )
    is_active: bool = Field(default=True, description="Whether job is active")

    # Optional Immich API filters
    album_ids: list[str] | None = Field(default=None, description="Filter by album UUIDs")
    person_ids: list[str] | None = Field(default=None, description="Filter by person UUIDs")
    tag_ids: list[str] | None = Field(default=None, description="Filter by tag UUIDs")
    is_favorite: bool | None = Field(default=None, description="Filter favorites only")
    city: str | None = Field(default=None, max_length=255, description="Filter by city")
    state: str | None = Field(default=None, max_length=255, description="Filter by state/region")
    country: str | None = Field(default=None, max_length=255, description="Filter by country")
    taken_after: datetime | None = Field(default=None, description="Photos taken after this date")
    taken_before: datetime | None = Field(default=None, description="Photos taken before this date")
    rating: int | None = Field(default=None, ge=0, le=5, description="Minimum rating (0-5)")


class ImmichSyncJobCreate(ImmichSyncJobBase):
    """API request model for creating sync jobs."""

    @model_validator(mode="after")
    def validate_smart_query(self) -> "ImmichSyncJobCreate":
        """Ensure query is provided when strategy is SMART."""
        if self.strategy == SyncStrategy.SMART and not self.query:
            raise ValueError("Query is required when strategy is SMART")
        return self


class ImmichSyncJobUpdate(BaseModel):
    """API request model for updating sync jobs.

    All fields are optional to allow partial updates.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    target_device_id: UUID | None = None
    strategy: SyncStrategy | None = None
    query: str | None = Field(default=None, max_length=500)
    count: int | None = Field(default=None, ge=1, le=1000)
    random_pick: bool | None = None
    overfetch_multiplier: int | None = Field(default=None, ge=1, le=10)
    min_color_score: float | None = Field(default=None, ge=0.0, le=1.0)
    is_active: bool | None = None

    # Optional Immich API filters
    album_ids: list[str] | None = None
    person_ids: list[str] | None = None
    tag_ids: list[str] | None = None
    is_favorite: bool | None = None
    city: str | None = Field(default=None, max_length=255)
    state: str | None = Field(default=None, max_length=255)
    country: str | None = Field(default=None, max_length=255)
    taken_after: datetime | None = None
    taken_before: datetime | None = None
    rating: int | None = Field(default=None, ge=0, le=5)


class ImmichSyncJobPublic(ImmichSyncJobBase):
    """API response model for sync jobs."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImmichSyncJobsPublic(BaseModel):
    """Paginated response for sync jobs."""

    data: list[ImmichSyncJobPublic]
    count: int
