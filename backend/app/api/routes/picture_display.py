"""Picture display API endpoints for image management with MinIO storage."""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from private_assistant_picture_display_skill.models.image import Image
from pydantic import BaseModel
from sqlalchemy import desc
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.api.schemas.picture_display import ImagePublic, ImagesPublic, ImageUpdate
from app.core.minio_client import MinIOClient
from app.models import Message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/picture-display", tags=["picture-display"])


class PresignedUrlResponse(BaseModel):
    """Response model for presigned URL."""

    url: str
    expires_in_seconds: int


@router.post("/images/upload", response_model=ImagePublic)
async def upload_image(  # noqa: PLR0913 - form fields require separate parameters
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    file: UploadFile = File(...),  # noqa: B008
    title: str | None = Form(None),
    description: str | None = Form(None),
    tags: str | None = Form(None),
    display_duration_seconds: int = Form(3600),
    priority: int = Form(0),
) -> Image:
    """Upload image to MinIO and create database record.

    Args:
        session: Database session
        current_user: Authenticated user
        file: Image file to upload
        title: Optional image title
        description: Optional image description
        tags: Optional comma-separated tags
        display_duration_seconds: Display duration (default 3600 seconds)
        priority: Display priority (default 0)

    Returns:
        Created image record

    Raises:
        HTTPException: If file validation fails or upload fails
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read and validate file size (max 10MB)
    file_data = await file.read()
    max_size = 10 * 1024 * 1024
    if len(file_data) > max_size:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    # Upload to MinIO
    try:
        storage_path = MinIOClient.upload_image(file_data, file.filename or "uploaded.jpg", file.content_type)
    except Exception as e:
        logger.error(f"MinIO upload failed: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed") from e

    # Create DB record using skill's Image model
    image = Image(
        source_name=file.filename or "uploaded",
        storage_path=storage_path,
        title=title,
        description=description,
        tags=tags,
        display_duration_seconds=display_duration_seconds,
        priority=priority,
    )
    session.add(image)
    await session.commit()
    await session.refresh(image)

    return image


@router.get("/images/", response_model=ImagesPublic)
async def read_images(
    session: SessionDep,
    _current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> ImagesPublic:
    """Retrieve images with pagination.

    Args:
        session: Database session
        current_user: Authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Paginated list of images
    """
    # Count total
    count_statement = select(func.count()).select_from(Image)
    count_result = await session.exec(count_statement)
    count = count_result.one()

    # Get paginated results
    # AIDEV-NOTE: Using col() for proper mypy typing with SQLModel
    statement = select(Image).order_by(desc(col(Image.created_at))).offset(skip).limit(limit)
    images_result: Any = await session.exec(statement)
    images = list(images_result.all())

    # Convert ORM models to Pydantic response models
    return ImagesPublic(
        data=[ImagePublic.model_validate(img) for img in images],
        count=count,
    )


@router.get("/images/{image_id}", response_model=ImagePublic)
async def read_image(session: SessionDep, _current_user: CurrentUser, image_id: uuid.UUID) -> Image:
    """Get image by ID.

    Args:
        session: Database session
        current_user: Authenticated user
        image_id: Image UUID

    Returns:
        Image record

    Raises:
        HTTPException: If image not found
    """
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.get("/images/{image_id}/url", response_model=PresignedUrlResponse)
async def get_image_url(
    session: SessionDep,
    _current_user: CurrentUser,
    image_id: uuid.UUID,
    expires_hours: int = 1,
) -> PresignedUrlResponse:
    """Get presigned URL for image access.

    Args:
        session: Database session
        current_user: Authenticated user
        image_id: Image UUID
        expires_hours: URL expiration time in hours (default: 1)

    Returns:
        Presigned URL and expiration time

    Raises:
        HTTPException: If image not found or URL generation fails
    """
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        url = MinIOClient.get_presigned_url(image.storage_path, expires_hours)
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate URL") from e

    return PresignedUrlResponse(url=url, expires_in_seconds=expires_hours * 3600)


@router.put("/images/{image_id}", response_model=ImagePublic)
async def update_image(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    image_id: uuid.UUID,
    image_in: ImageUpdate,
) -> Image:
    """Update image metadata.

    Args:
        session: Database session
        current_user: Authenticated user
        image_id: Image UUID
        image_in: Updated image metadata

    Returns:
        Updated image record

    Raises:
        HTTPException: If image not found
    """
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    update_dict = image_in.model_dump(exclude_unset=True)
    image.sqlmodel_update(update_dict)

    # Update timestamp
    image.updated_at = datetime.now()

    session.add(image)
    await session.commit()
    await session.refresh(image)

    return image


@router.delete("/images/{image_id}")
async def delete_image(session: SessionDep, _current_user: CurrentUser, image_id: uuid.UUID) -> Message:
    """Delete image from MinIO and database.

    Args:
        session: Database session
        current_user: Authenticated user
        image_id: Image UUID

    Returns:
        Success message

    Raises:
        HTTPException: If image not found
    """
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete from MinIO first
    try:
        MinIOClient.delete_image(image.storage_path)
    except Exception as e:
        logger.warning(f"MinIO deletion failed (continuing): {e}")

    # Delete from database
    await session.delete(image)
    await session.commit()

    return Message(message="Image deleted successfully")
