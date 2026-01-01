"""Application pre-start: database readiness, migrations, and initial data."""

import asyncio
import logging

from alembic import command
from alembic.config import Config
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import get_engine, init_db

logger = logging.getLogger(__name__)

MAX_TRIES = 60 * 5  # 5 minutes
WAIT_SECONDS = 1


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def wait_for_db() -> None:
    """Wait for database to be ready with retry logic."""
    async with AsyncSession(get_engine()) as session:
        await session.exec(select(1))


def run_migrations() -> None:
    """Run alembic migrations programmatically.

    Note: This runs synchronously because alembic's env.py uses asyncio.run()
    internally, which cannot be called from within an existing event loop.
    """
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def create_initial_data() -> None:
    """Create initial data (superuser) if not exists."""
    async with AsyncSession(get_engine()) as session:
        await init_db(session)


def main() -> None:
    """Run all pre-start tasks.

    Runs DB wait and init data as async, but migrations synchronously
    because alembic's env.py already handles its own async loop.

    Note: We clear the engine cache between asyncio.run() calls because
    each creates a new event loop, and the cached engine's connection pool
    is tied to a specific event loop.
    """
    logger.info("Waiting for database...")
    asyncio.run(wait_for_db())
    get_engine.cache_clear()  # Clear engine cache before alembic creates its own loop
    logger.info("Database is ready")

    logger.info("Running database migrations...")
    run_migrations()
    get_engine.cache_clear()  # Clear again after alembic's loop
    logger.info("Migrations complete")

    logger.info("Creating initial data...")
    asyncio.run(create_initial_data())
    logger.info("Initial data created")

    logger.info("Pre-start complete")


if __name__ == "__main__":
    main()
