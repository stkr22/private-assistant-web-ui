"""Security utilities for JWT token validation and password hashing."""

import base64
import json
import logging
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any, Literal

from joserfc import jwt as joserfc_jwt
from joserfc.errors import JoseError
from joserfc.jwk import KeySet, OctKey
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.jwks_client import OAuthJWKSClient

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
JWT_PARTS_COUNT = 3
BASE64_PADDING_MODULUS = 4

# Token type literals
TokenTypeValue = Literal["local", "oauth"]


class TokenType:
    """Token type enumeration."""

    LOCAL: TokenTypeValue = "local"
    OAUTH: TokenTypeValue = "oauth"


@lru_cache(maxsize=1)
def _get_local_key() -> OctKey:
    """Get or create the symmetric key for local JWT operations."""
    return OctKey.import_key(get_settings().SECRET_KEY)


def detect_token_type(token: str) -> TokenTypeValue:
    """Detect token type by inspecting issuer claim (no validation)."""
    try:
        # JWT format is: header.payload.signature
        parts = token.split(".")
        if len(parts) != JWT_PARTS_COUNT:
            logger.debug("Token does not have 3 parts, treating as local")
            return TokenType.LOCAL

        # Decode the payload (second part) - add padding if needed
        payload_b64 = parts[1]
        padding = BASE64_PADDING_MODULUS - (len(payload_b64) % BASE64_PADDING_MODULUS)
        if padding != BASE64_PADDING_MODULUS:
            payload_b64 += "=" * padding

        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes)

        issuer = payload.get("iss")
        settings = get_settings()
        if issuer and settings.oauth.ISSUER and issuer.rstrip("/") == settings.oauth.ISSUER.rstrip("/"):
            logger.debug(f"Detected OAuth token from issuer: {issuer}")
            return TokenType.OAUTH

        logger.debug("Detected local token")
        return TokenType.LOCAL
    except Exception as e:
        logger.warning(f"Error detecting token type: {e}, defaulting to local")
        return TokenType.LOCAL


def validate_local_token(token: str) -> dict[str, Any]:
    """Validate local HS256 JWT token using joserfc."""
    try:
        token_obj = joserfc_jwt.decode(token, _get_local_key())
        return dict(token_obj.claims)
    except JoseError as e:
        raise ValueError(f"Local token validation failed: {e}") from e


async def validate_oauth_token(token: str) -> dict[str, Any]:
    """Validate OAuth JWT using joserfc and JWKS.

    This function:
    1. Fetches JWKS from the OAuth provider (with caching)
    2. Uses joserfc to decode and validate the JWT
    3. Verifies issuer, expiration, subject, and optionally audience
    """
    settings = get_settings()
    if settings.DISABLE_OAUTH or not settings.oauth.ISSUER:
        raise ValueError("OAuth is disabled or not configured")

    # Fetch JWKS from provider
    try:
        jwks_data = await OAuthJWKSClient.get_instance().fetch_jwks()
        logger.debug(f"JWKS fetched with {len(jwks_data.get('keys', []))} keys")
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise ValueError(f"Failed to fetch JWKS: {e}") from e

    # Import the key set
    try:
        key_set = KeySet.import_key_set(jwks_data)  # type: ignore[arg-type]
    except Exception as e:
        logger.error(f"Failed to import JWKS key set: {e}")
        raise ValueError(f"Invalid JWKS format: {e}") from e

    try:
        # Decode token (signature verification)
        token_obj = joserfc_jwt.decode(token, key_set)

        # Build claims registry for validation
        claims_registry = joserfc_jwt.JWTClaimsRegistry(
            iss={"essential": True, "value": settings.oauth.ISSUER},
            sub={"essential": True},
            leeway=120,  # 2 minutes clock skew tolerance
        )

        # Validate claims (iss, sub, exp, nbf, iat)
        claims_registry.validate(token_obj.claims)

        # Check audience if configured
        if settings.oauth.CLIENT_ID:
            aud = token_obj.claims.get("aud")
            if aud:
                aud_list = aud if isinstance(aud, list) else [aud]
                if settings.oauth.CLIENT_ID not in aud_list:
                    raise JoseError("Invalid audience")

        logger.info(f"OAuth token validated successfully for sub={token_obj.claims.get('sub')}")
        return dict(token_obj.claims)
    except JoseError as e:
        logger.error(f"OAuth token validation failed: {e}")
        raise ValueError(f"OAuth token validation failed: {e}") from e


async def validate_token(token: str) -> tuple[dict[str, Any], TokenTypeValue]:
    """Validate JWT token (auto-detect local vs OAuth)."""
    token_type = detect_token_type(token)

    if token_type == TokenType.OAUTH:
        payload = await validate_oauth_token(token)
        return payload, TokenType.OAUTH
    payload = validate_local_token(token)
    return payload, TokenType.LOCAL


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """Create a local HS256 JWT token using joserfc."""
    expire = datetime.now(UTC) + expires_delta
    # joserfc expects exp as Unix timestamp
    claims = {"exp": int(expire.timestamp()), "sub": str(subject)}
    return joserfc_jwt.encode({"alg": ALGORITHM}, claims, _get_local_key())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)
