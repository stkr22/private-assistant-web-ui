"""
Script to create all database tables.

This includes both web-ui specific tables and commons tables from
the private-assistant-commons package.

Usage:
    uv run python create_tables.py
"""

import asyncio

# Import commons models
from private_assistant_commons.database.models import (  # noqa: F401
    DeviceType,
    GlobalDevice,
    Room,
    Skill,
)

# Import picture display models from skill package
from private_assistant_picture_display_skill.models.device import (  # noqa: F401
    DeviceDisplayState,
)
from private_assistant_picture_display_skill.models.image import Image  # noqa: F401
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app.core.config import get_settings

# Import all models to register them with SQLModel metadata
from app.models import User  # noqa: F401


async def create_tables():
    """Create all database tables."""
    engine = create_async_engine(str(get_settings().SQLALCHEMY_DATABASE_URI), echo=True)

    async with engine.begin() as conn:
        # Create all tables defined in SQLModel metadata
        await conn.run_sync(SQLModel.metadata.create_all)

    await engine.dispose()

    print("All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
