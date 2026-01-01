"""JWKS client for fetching and caching OAuth provider public keys."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class OAuthJWKSClient:
    """Manages JWKS fetching and caching for OAuth providers."""

    _instance: OAuthJWKSClient | None = None

    def __init__(self) -> None:
        self._keys: dict | None = None
        self._fetched_at: datetime | None = None
        self._cache_duration = timedelta(hours=1)

    @classmethod
    def get_instance(cls) -> OAuthJWKSClient:
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_jwks_url(self) -> str:
        """Build JWKS URL from OAuth provider issuer."""
        if not settings.OAUTH_ISSUER:
            raise ValueError("OAUTH_ISSUER not configured")
        # Zitadel uses /oauth/v2/keys instead of standard /.well-known/jwks.json
        return f"{settings.OAUTH_ISSUER}/oauth/v2/keys"

    async def fetch_jwks(self) -> dict:
        """Fetch JWKS from OAuth provider with caching."""
        now = datetime.now()

        # Return cached keys if still valid
        if self._keys and self._fetched_at and now - self._fetched_at < self._cache_duration:
            logger.debug("Using cached JWKS keys")
            return self._keys

        # Fetch fresh keys
        jwks_url = self._get_jwks_url()
        logger.info(f"Fetching JWKS from {jwks_url}")

        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            response.raise_for_status()
            self._keys = response.json()
            self._fetched_at = now
            logger.info(f"Fetched {len(self._keys.get('keys', []))} keys from JWKS")
            return self._keys

    def clear_cache(self) -> None:
        """Clear the cached JWKS keys."""
        self._keys = None
        self._fetched_at = None
        logger.info("JWKS cache cleared")
