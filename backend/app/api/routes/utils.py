"""Utility API routes."""

from fastapi import APIRouter

from app.api.schemas.health import HealthResponse

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint.

    Returns a simple status response to indicate the service is running.

    Returns:
        HealthResponse: Current health status.
    """
    return HealthResponse()
