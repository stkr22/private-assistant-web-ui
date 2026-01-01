"""Monitoring API endpoints for skills and commands."""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter
from private_assistant_commons.database.models import Skill
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class SkillPublic(BaseModel):
    """Public schema for Skill."""

    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class SkillsPublic(BaseModel):
    """Paginated response for skills."""

    data: list[SkillPublic]
    count: int


@router.get("/skills", response_model=SkillsPublic)
async def read_skills(session: SessionDep, _current_user: CurrentUser) -> SkillsPublic:
    """List all registered skills."""
    statement = select(Skill).order_by(Skill.name)
    result = await session.exec(statement)
    skills = result.all()

    # Convert to public schema
    skills_public = [
        SkillPublic(
            id=skill.id,
            name=skill.name,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )
        for skill in skills
    ]

    return SkillsPublic(data=skills_public, count=len(skills_public))
