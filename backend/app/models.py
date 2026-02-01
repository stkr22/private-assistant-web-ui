"""Database models and schemas."""

import uuid

# Import picture display models from skill package to register with SQLModel
from private_assistant_picture_display_skill.models.device import DeviceDisplayState  # noqa: F401
from private_assistant_picture_display_skill.models.image import Image  # noqa: F401
from private_assistant_picture_display_skill.models.immich_sync_job import ImmichSyncJob  # noqa: F401
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Shared user properties."""

    email: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(min_length=8, max_length=128)


class User(UserBase, table=True):
    """User database model."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = None
    oauth_provider: str | None = Field(default=None, max_length=50)
    oauth_subject: str | None = Field(default=None, max_length=255, index=True, unique=True)


class UserPublic(UserBase):
    """User public API schema."""

    id: uuid.UUID


class UsersPublic(SQLModel):
    """Paginated users response."""

    data: list[UserPublic]
    count: int


class Message(SQLModel):
    """Generic message response."""

    message: str


class Token(SQLModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """JWT token payload."""

    sub: str | None = None
