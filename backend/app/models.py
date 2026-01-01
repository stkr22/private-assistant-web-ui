import uuid

from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = None
    oauth_provider: str | None = Field(default=None, max_length=50)
    oauth_subject: str | None = Field(default=None, max_length=255, index=True, unique=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


# Import picture display models from skill package to register with SQLModel
# AIDEV-NOTE: These imports ensure that the table models are registered
# with SQLModel's metadata for Alembic migrations
from private_assistant_picture_display_skill.models.device import (  # noqa: F401, E402
    DeviceDisplayState,
)
from private_assistant_picture_display_skill.models.image import Image  # noqa: F401, E402
