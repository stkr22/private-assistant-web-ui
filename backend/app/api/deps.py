import logging
from collections.abc import AsyncGenerator
from http import HTTPStatus
from typing import Annotated, Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from joserfc.errors import JoseError
from pydantic import ValidationError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.db import get_engine
from app.models import TokenPayload, User

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(get_engine()) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Get current user from JWT token (local or OAuth)."""
    logger.debug(f"Validating token (length={len(token)}, dots={token.count('.')})")
    try:
        payload, token_type = await security.validate_token(token)
        logger.debug(f"Token validated as type: {token_type}")
    except (ValidationError, ValueError, JoseError) as e:
        logger.error(f"Token validation failed: {type(e).__name__}: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {e!s}",
        ) from e

    if token_type == security.TokenType.LOCAL:
        # Local token: 'sub' is user UUID
        token_data = TokenPayload(**payload)
        user = await session.get(User, token_data.sub)
    else:
        # OAuth token: look up or create OAuth user
        user = await _get_or_create_oauth_user(session, payload, token)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def _get_or_create_oauth_user(session: AsyncSession, oauth_payload: dict[str, Any], token: str) -> User | None:
    """Get or create user from OAuth token payload.

    If email is not in the token, fetches it from the userinfo endpoint.
    """
    if settings.DISABLE_OAUTH:
        raise HTTPException(status_code=400, detail="OAuth authentication is disabled")

    oauth_subject = oauth_payload.get("sub")
    if not oauth_subject:
        raise HTTPException(status_code=400, detail="Invalid OAuth token: missing sub claim")

    # Look up by oauth_subject first (existing user)
    statement = select(User).where(User.oauth_subject == oauth_subject)
    result = await session.exec(statement)
    user = result.first()

    if user:
        return user

    # New user - need email for provisioning
    email = oauth_payload.get("email")
    full_name = oauth_payload.get("name")

    # If email not in token, fetch from userinfo endpoint
    if not email and settings.OAUTH_ISSUER:
        userinfo_url = f"{settings.OAUTH_ISSUER}/oidc/v1/userinfo"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    userinfo_url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )
                if response.status_code == HTTPStatus.OK:
                    userinfo = response.json()
                    email = userinfo.get("email")
                    if not full_name:
                        full_name = userinfo.get("name")
                    logger.info(f"Fetched userinfo for sub={oauth_subject}: email={email}")
                else:
                    logger.warning(f"Failed to fetch userinfo: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error fetching userinfo: {e}")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Could not determine email for OAuth user. Ensure 'email' scope is requested.",
        )

    # Extract provider name from issuer
    provider = "oauth"
    if settings.OAUTH_ISSUER:
        issuer_parts = settings.OAUTH_ISSUER.rstrip("/").split("//")[-1].split("/")[0]
        provider = issuer_parts.replace("www.", "")

    new_user = User(
        email=email,
        full_name=full_name,
        oauth_provider=provider,
        oauth_subject=oauth_subject,
        hashed_password=None,
        is_active=True,
        is_superuser=False,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    logger.info(f"Auto-provisioned new OAuth user: {email} (provider={provider})")

    return new_user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user
