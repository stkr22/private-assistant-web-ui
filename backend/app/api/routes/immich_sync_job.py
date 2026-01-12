"""API routes for ImmichSyncJob management."""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from private_assistant_picture_display_skill.models.immich_sync_job import (
    ImmichSyncJob,
    SyncStrategy,
)
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.api.schemas.immich_sync_job import (
    ImmichSyncJobCreate,
    ImmichSyncJobPublic,
    ImmichSyncJobsPublic,
    ImmichSyncJobUpdate,
)
from app.models import Message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/immich-sync-jobs", tags=["immich-sync-jobs"])


def _handle_integrity_error(e: IntegrityError) -> None:
    """Convert database IntegrityError to appropriate HTTPException."""
    error_msg = str(e.orig).lower() if e.orig else str(e).lower()
    if "unique" in error_msg or "duplicate" in error_msg:
        raise HTTPException(status_code=400, detail="A sync job with this name already exists")
    if "foreign key" in error_msg or "fk_" in error_msg:
        raise HTTPException(status_code=400, detail="Target device not found")
    raise HTTPException(status_code=400, detail="Database constraint violation")


@router.get("/", response_model=ImmichSyncJobsPublic)
async def read_sync_jobs(
    session: SessionDep,
    _current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> ImmichSyncJobsPublic:
    """Retrieve Immich sync jobs with pagination.

    Args:
        session: Database session
        current_user: Authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Paginated list of sync jobs
    """
    # Count total
    count_statement = select(func.count()).select_from(ImmichSyncJob)
    count_result = await session.exec(count_statement)
    count = count_result.one()

    # Get paginated results ordered by name
    # AIDEV-NOTE: Using col() for proper mypy typing with SQLModel
    statement = select(ImmichSyncJob).order_by(col(ImmichSyncJob.name)).offset(skip).limit(limit)
    result: Any = await session.exec(statement)
    jobs = list(result.all())

    return ImmichSyncJobsPublic(
        data=[ImmichSyncJobPublic.model_validate(job) for job in jobs],
        count=count,
    )


@router.get("/{job_id}", response_model=ImmichSyncJobPublic)
async def read_sync_job(
    session: SessionDep,
    _current_user: CurrentUser,
    job_id: uuid.UUID,
) -> ImmichSyncJob:
    """Get sync job by ID.

    Args:
        session: Database session
        current_user: Authenticated user
        job_id: Sync job UUID

    Returns:
        Sync job record

    Raises:
        HTTPException: If sync job not found
    """
    job = await session.get(ImmichSyncJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Sync job not found")
    return job


@router.post("/", response_model=ImmichSyncJobPublic)
async def create_sync_job(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    job_in: ImmichSyncJobCreate,
) -> ImmichSyncJob:
    """Create new Immich sync job.

    Args:
        session: Database session
        current_user: Authenticated user
        job_in: Sync job creation data

    Returns:
        Created sync job record

    Raises:
        HTTPException: If validation fails (duplicate name, device not found, etc.)
    """
    job = ImmichSyncJob.model_validate(job_in)
    session.add(job)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        _handle_integrity_error(e)
    await session.refresh(job)
    return job


@router.put("/{job_id}", response_model=ImmichSyncJobPublic)
async def update_sync_job(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    job_id: uuid.UUID,
    job_in: ImmichSyncJobUpdate,
) -> ImmichSyncJob:
    """Update an Immich sync job.

    Args:
        session: Database session
        current_user: Authenticated user
        job_id: Sync job UUID
        job_in: Updated sync job data

    Returns:
        Updated sync job record

    Raises:
        HTTPException: If sync job not found or validation fails
    """
    job = await session.get(ImmichSyncJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Sync job not found")

    update_dict = job_in.model_dump(exclude_unset=True)

    # Validate query requirement for SMART strategy (business logic not enforced by DB)
    new_strategy = update_dict.get("strategy", job.strategy)
    new_query = update_dict.get("query", job.query)
    if new_strategy == SyncStrategy.SMART and not new_query:
        raise HTTPException(status_code=400, detail="Query is required when strategy is SMART")

    job.sqlmodel_update(update_dict)
    job.updated_at = datetime.now()

    session.add(job)
    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        _handle_integrity_error(e)
    await session.refresh(job)
    return job


@router.delete("/{job_id}")
async def delete_sync_job(
    session: SessionDep,
    _current_user: CurrentUser,
    job_id: uuid.UUID,
) -> Message:
    """Delete an Immich sync job.

    Args:
        session: Database session
        current_user: Authenticated user
        job_id: Sync job UUID

    Returns:
        Success message

    Raises:
        HTTPException: If sync job not found
    """
    job = await session.get(ImmichSyncJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Sync job not found")

    await session.delete(job)
    await session.commit()

    return Message(message="Sync job deleted successfully")
