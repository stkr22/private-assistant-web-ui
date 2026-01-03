"""Health check response schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model.

    Attributes:
        status: Current health status of the application.
    """

    status: str = Field(default="ok", description="Health status of the application")
