"""Application configuration settings."""

import secrets
import warnings
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from string or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    if isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        # Use backend .env file (relative to CWD when app runs from backend/)
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    LOG_LEVEL: str = "INFO"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """Get all CORS origins including frontend host."""
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:  # noqa: N802
        """Build PostgreSQL database URI."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # User management
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # MQTT Configuration
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str | None = None
    MQTT_PASSWORD: str | None = None

    # MinIO Configuration
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "assistant-images"
    MINIO_SECURE: bool = False

    # OAuth Configuration (Generic OIDC - works with any provider)
    DISABLE_OAUTH: bool = False  # Set to True to disable OAuth
    OAUTH_ISSUER: str | None = None  # OAuth provider issuer URL (e.g., https://accounts.google.com)
    OAUTH_CLIENT_ID: str | None = None  # OAuth client ID
    OAUTH_CLIENT_SECRET: str | None = None  # OAuth client secret (optional for PKCE)

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """Check if a secret value is the default 'changethis' value."""
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", for security, please change it, at least for deployments.'
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """Enforce that default secrets are changed in non-local environments."""
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
        return self

    @model_validator(mode="after")
    def _validate_oauth_config(self) -> Self:
        """Validate OAuth configuration when enabled."""
        if not self.DISABLE_OAUTH:
            if not self.OAUTH_ISSUER:
                raise ValueError("OAUTH_ISSUER required when DISABLE_OAUTH=false")
            if not self.OAUTH_CLIENT_ID:
                raise ValueError("OAUTH_CLIENT_ID required when DISABLE_OAUTH=false")
        return self


settings = Settings()  # type: ignore
