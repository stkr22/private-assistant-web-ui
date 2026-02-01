"""Monitoring API endpoints for skills and commands."""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter
from private_assistant_commons.database.intent_pattern_models import IntentPattern
from private_assistant_commons.database.skill_models import Skill, SkillIntent
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class IntentPatternPublic(BaseModel):
    """Public schema for IntentPattern in monitoring context."""

    id: uuid.UUID
    intent_type: str
    description: str | None = None
    priority: int
    enabled: bool


class SkillPublic(BaseModel):
    """Public schema for Skill with supported intent patterns."""

    id: uuid.UUID
    name: str
    help_text: str | None = None
    created_at: datetime
    updated_at: datetime
    intent_patterns: list[IntentPatternPublic] = []


class SkillsPublic(BaseModel):
    """Paginated response for skills."""

    data: list[SkillPublic]
    count: int


@router.get("/skills")
async def read_skills(session: SessionDep, _current_user: CurrentUser) -> SkillsPublic:
    """List all registered skills with their supported intent patterns."""
    statement = select(Skill).order_by(Skill.name)  # type: ignore[attr-defined]
    result = await session.exec(statement)  # type: ignore[arg-type]
    skills = result.all()

    # Convert to public schema with intent patterns
    skills_public = []
    for skill in skills:
        # Load intent patterns for this skill
        skill_intent_statement = select(SkillIntent).where(SkillIntent.skill_id == skill.id)  # type: ignore[attr-defined]
        skill_intent_result = await session.exec(skill_intent_statement)  # type: ignore[arg-type]
        skill_intents = skill_intent_result.all()

        # Load the actual intent pattern details
        intent_patterns_public = []
        for skill_intent in skill_intents:
            pattern = await session.get(IntentPattern, skill_intent.intent_pattern_id)
            if pattern:
                intent_patterns_public.append(
                    IntentPatternPublic(
                        id=pattern.id,
                        intent_type=pattern.intent_type,
                        description=pattern.description,
                        priority=pattern.priority,
                        enabled=pattern.enabled,
                    )
                )

        skills_public.append(
            SkillPublic(
                id=skill.id,
                name=skill.name,
                help_text=skill.help_text,
                created_at=skill.created_at,
                updated_at=skill.updated_at,
                intent_patterns=intent_patterns_public,
            )
        )

    return SkillsPublic(data=skills_public, count=len(skills_public))
