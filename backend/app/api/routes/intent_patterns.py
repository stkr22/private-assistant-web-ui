"""API routes for IntentPattern management with nested keywords."""

import logging
import uuid

from fastapi import APIRouter, HTTPException
from private_assistant_commons.database.intent_pattern_models import IntentPattern, IntentPatternKeyword
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.models_commons_api import (
    IntentPatternCreate,
    IntentPatternPublic,
    IntentPatternsPublic,
    IntentPatternUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/intent-patterns", tags=["intent-patterns"])


@router.get("/")
async def read_intent_patterns(
    session: SessionDep, _current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> IntentPatternsPublic:
    """Retrieve intent patterns with pagination and nested keywords."""
    # Get count
    count_statement = select(func.count()).select_from(IntentPattern)
    result = await session.exec(count_statement)
    count = result.one()

    # Get patterns ordered by priority (higher first)
    statement = select(IntentPattern).offset(skip).limit(limit).order_by(IntentPattern.priority.desc())  # type: ignore[attr-defined]
    result = await session.exec(statement)  # type: ignore[arg-type]
    patterns = result.all()

    # Manually load keywords for each pattern
    patterns_with_keywords = []
    for pattern in patterns:
        keyword_statement = select(IntentPatternKeyword).where(IntentPatternKeyword.pattern_id == pattern.id)  # type: ignore[attr-defined]
        keyword_result = await session.exec(keyword_statement)  # type: ignore[arg-type]
        keywords = keyword_result.all()

        # Build public response
        pattern_dict = pattern.model_dump()  # type: ignore[attr-defined]
        pattern_dict["keywords"] = [kw.model_dump() for kw in keywords]
        patterns_with_keywords.append(pattern_dict)

    return IntentPatternsPublic(data=patterns_with_keywords, count=count)


@router.get("/{pattern_id}")
async def read_intent_pattern(
    session: SessionDep, _current_user: CurrentUser, pattern_id: uuid.UUID
) -> IntentPatternPublic:
    """Get intent pattern by ID with keywords."""
    pattern = await session.get(IntentPattern, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Intent pattern not found")

    # Load keywords
    keyword_statement = select(IntentPatternKeyword).where(IntentPatternKeyword.pattern_id == pattern.id)  # type: ignore[attr-defined]
    keyword_result = await session.exec(keyword_statement)  # type: ignore[arg-type]
    keywords = keyword_result.all()

    # Build response
    pattern_dict = pattern.model_dump()  # type: ignore[attr-defined]
    pattern_dict["keywords"] = [kw.model_dump() for kw in keywords]
    return pattern_dict  # type: ignore[return-value]


@router.post("/")
async def create_intent_pattern(
    *, session: SessionDep, _current_user: CurrentUser, pattern_in: IntentPatternCreate
) -> IntentPatternPublic:
    """Create new intent pattern with keywords."""
    # Create pattern
    pattern_data = pattern_in.model_dump(exclude={"keywords"})
    pattern = IntentPattern.model_validate(pattern_data)
    session.add(pattern)
    await session.commit()
    await session.refresh(pattern)

    # Create keywords
    keywords = []
    for keyword_data in pattern_in.keywords:
        keyword = IntentPatternKeyword(pattern_id=pattern.id, **keyword_data.model_dump())
        session.add(keyword)
        keywords.append(keyword)

    await session.commit()
    for kw in keywords:
        await session.refresh(kw)

    # Build response
    pattern_dict = pattern.model_dump()
    pattern_dict["keywords"] = [kw.model_dump() for kw in keywords]
    return pattern_dict  # type: ignore[return-value]


@router.put("/{pattern_id}")
async def update_intent_pattern(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    pattern_id: uuid.UUID,
    pattern_in: IntentPatternUpdate,
) -> IntentPatternPublic:
    """Update intent pattern and optionally replace all keywords."""
    pattern = await session.get(IntentPattern, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Intent pattern not found")

    # Update pattern fields
    update_dict = pattern_in.model_dump(exclude_unset=True, exclude={"keywords"})
    pattern.sqlmodel_update(update_dict)
    session.add(pattern)

    # Handle keywords if provided (replace all)
    if pattern_in.keywords is not None:
        # Delete existing keywords
        delete_statement = select(IntentPatternKeyword).where(IntentPatternKeyword.pattern_id == pattern_id)
        existing_keywords = await session.exec(delete_statement)  # type: ignore[arg-type]
        for kw in existing_keywords:
            await session.delete(kw)

        # Create new keywords
        keywords = []
        for keyword_data in pattern_in.keywords:
            keyword = IntentPatternKeyword(pattern_id=pattern.id, **keyword_data.model_dump())
            session.add(keyword)
            keywords.append(keyword)
    else:
        # Load existing keywords
        keyword_statement = select(IntentPatternKeyword).where(IntentPatternKeyword.pattern_id == pattern_id)
        keyword_result = await session.exec(keyword_statement)  # type: ignore[arg-type]
        keywords = list(keyword_result.all())

    await session.commit()
    await session.refresh(pattern)
    for kw in keywords:
        await session.refresh(kw)

    # Build response
    pattern_dict = pattern.model_dump()
    pattern_dict["keywords"] = [kw.model_dump() for kw in keywords]
    return pattern_dict  # type: ignore[return-value]


@router.delete("/{pattern_id}")
async def delete_intent_pattern(session: SessionDep, _current_user: CurrentUser, pattern_id: uuid.UUID) -> Message:
    """Delete intent pattern (keywords cascade delete)."""
    pattern = await session.get(IntentPattern, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Intent pattern not found")

    await session.delete(pattern)
    await session.commit()
    return Message(message="Intent pattern deleted successfully")
