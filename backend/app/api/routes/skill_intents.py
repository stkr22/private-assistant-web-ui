"""API routes for SkillIntent management (read-only)."""

import logging
import uuid

from fastapi import APIRouter
from private_assistant_commons.database.skill_models import SkillIntent
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models_commons_api import SkillIntentsPublic

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/skill-intents", tags=["skill-intents"])


@router.get("/")
async def read_skill_intents(
    session: SessionDep, _current_user: CurrentUser, skill_id: uuid.UUID | None = None, skip: int = 0, limit: int = 100
) -> SkillIntentsPublic:
    """Retrieve skill-intent mappings with optional skill filter.

    Skills auto-register their intents, so this endpoint is read-only.
    """
    # Build base query
    base_query = select(SkillIntent)
    if skill_id:
        base_query = base_query.where(SkillIntent.skill_id == skill_id)

    # Get count
    count_statement = select(func.count()).select_from(base_query.subquery())
    result = await session.exec(count_statement)
    count = result.one()

    # Get data
    statement = base_query.offset(skip).limit(limit)
    result = await session.exec(statement)  # type: ignore[arg-type]
    skill_intents = result.all()

    return SkillIntentsPublic(data=list(skill_intents), count=count)
