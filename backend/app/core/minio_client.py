"""MinIO client for image storage."""

import logging
import uuid
from datetime import timedelta
from io import BytesIO
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MinIOClient:
    """Singleton MinIO client for image storage.

    AIDEV-NOTE: MinIO provides S3-compatible object storage for images.
    Presigned URLs are generated for frontend access with configurable expiration.
    """

    _instance: Minio | None = None

    @classmethod
    def get_client(cls) -> Minio:
        """Get or create MinIO client instance.

        Returns:
            Configured MinIO client with bucket initialization.

        Raises:
            S3Error: If bucket creation or verification fails.
        """
        if cls._instance is None:
            settings = get_settings()
            client = Minio(
                settings.minio.ENDPOINT,
                access_key=settings.minio.ACCESS_KEY,
                secret_key=settings.minio.SECRET_KEY,
                secure=settings.minio.SECURE,
            )

            # Ensure bucket exists
            try:
                if not client.bucket_exists(settings.minio.BUCKET_NAME):
                    client.make_bucket(settings.minio.BUCKET_NAME)
                    logger.info(f"Created MinIO bucket: {settings.minio.BUCKET_NAME}")
                else:
                    logger.info(f"MinIO bucket already exists: {settings.minio.BUCKET_NAME}")
            except S3Error as e:
                logger.error(f"Failed to initialize MinIO bucket: {e}")
                raise

            cls._instance = client

        return cls._instance

    @classmethod
    def upload_image(cls, file_data: bytes, file_name: str, content_type: str = "image/jpeg") -> str:
        """Upload image to MinIO.

        Args:
            file_data: Binary image data.
            file_name: Original filename.
            content_type: MIME type of the image.

        Returns:
            Storage path (object name in bucket).

        Raises:
            S3Error: If upload fails.
        """
        client = cls.get_client()
        settings = get_settings()

        # Generate unique storage path
        file_ext = Path(file_name).suffix or ".jpg"
        storage_path = f"images/{uuid.uuid4()}{file_ext}"

        try:
            client.put_object(
                settings.minio.BUCKET_NAME,
                storage_path,
                BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )

            logger.info(f"Uploaded image to MinIO: {storage_path}")
            return storage_path

        except S3Error as e:
            logger.error(f"Failed to upload image to MinIO: {e}")
            raise

    @classmethod
    def delete_image(cls, storage_path: str) -> None:
        """Delete image from MinIO.

        Args:
            storage_path: Object name in bucket.

        Raises:
            S3Error: If deletion fails.
        """
        client = cls.get_client()
        settings = get_settings()

        try:
            client.remove_object(settings.minio.BUCKET_NAME, storage_path)
            logger.info(f"Deleted image from MinIO: {storage_path}")
        except S3Error as e:
            logger.error(f"Failed to delete image from MinIO: {e}")
            raise

    @classmethod
    def get_presigned_url(cls, storage_path: str, expires_hours: int = 1) -> str:
        """Get presigned URL for image access.

        Args:
            storage_path: Object name in bucket.
            expires_hours: URL expiration time in hours (default: 1).

        Returns:
            Presigned URL for image download.

        Raises:
            S3Error: If URL generation fails.
        """
        client = cls.get_client()
        settings = get_settings()

        try:
            url = client.presigned_get_object(
                settings.minio.BUCKET_NAME,
                storage_path,
                expires=timedelta(hours=expires_hours),
            )
            logger.debug(f"Generated presigned URL for: {storage_path}")
            return url
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
