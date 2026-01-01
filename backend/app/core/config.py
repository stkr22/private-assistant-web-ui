"""Application configuration settings."""

import secrets
import warnings
from functools import lru_cache
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    Field,
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


class PostgresSettings(BaseSettings):
    """PostgreSQL database connection settings."""

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    HOST: str
    PORT: int = 5432
    USER: str
    PASSWORD: str = ""
    DB: str = ""


class MQTTSettings(BaseSettings):
    """MQTT broker connection settings."""

    model_config = SettingsConfigDict(
        env_prefix="MQTT_",
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    HOST: str = "localhost"
    PORT: int = 1883
    USERNAME: str | None = None
    PASSWORD: str | None = None


class MinIOSettings(BaseSettings):
    """MinIO object storage settings."""

    model_config = SettingsConfigDict(
        env_prefix="MINIO_",
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENDPOINT: str = "localhost:9000"
    ACCESS_KEY: str = "minioadmin"
    SECRET_KEY: str = "minioadmin"
    BUCKET_NAME: str = "assistant-images"
    SECURE: bool = False


class OAuthSettings(BaseSettings):
    """OAuth/OIDC authentication settings."""

    model_config = SettingsConfigDict(
        env_prefix="OAUTH_",
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ISSUER: str | None = None
    CLIENT_ID: str | None = None
    CLIENT_SECRET: str | None = None


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Core app settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    LOG_LEVEL: str = "INFO"
    PROJECT_NAME: str
    DISABLE_OAUTH: bool = False

    # User management
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # CORS configuration
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    # Nested settings (delayed instantiation)
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    mqtt: MQTTSettings = Field(default_factory=MQTTSettings)
    minio: MinIOSettings = Field(default_factory=MinIOSettings)
    oauth: OAuthSettings = Field(default_factory=OAuthSettings)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """Get all CORS origins including frontend host."""
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:  # noqa: N802
        """Build PostgreSQL database URI."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres.USER,
            password=self.postgres.PASSWORD,
            host=self.postgres.HOST,
            port=self.postgres.PORT,
            path=self.postgres.DB,
        )

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
        self._check_default_secret("POSTGRES_PASSWORD", self.postgres.PASSWORD)
        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD)
        return self

    @model_validator(mode="after")
    def _validate_oauth_config(self) -> Self:
        """Validate OAuth configuration when enabled."""
        if not self.DISABLE_OAUTH:
            if not self.oauth.ISSUER:
                raise ValueError("OAUTH_ISSUER required when DISABLE_OAUTH=false")
            if not self.oauth.CLIENT_ID:
                raise ValueError("OAUTH_CLIENT_ID required when DISABLE_OAUTH=false")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings instance.

    Uses lru_cache to ensure singleton behavior while allowing
    dependency injection and cache clearing for testing.

    Returns:
        Configured Settings instance.
    """
    return Settings()
