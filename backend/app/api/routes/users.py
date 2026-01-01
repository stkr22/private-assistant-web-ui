"""User management API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    User,
    UserPublic,
    UsersPublic,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve users."""
    count_statement = select(func.count()).select_from(User)
    result = await session.exec(count_statement)
    count = result.one()

    statement = select(User).offset(skip).limit(limit)
    result = await session.exec(statement)  # type: ignore[arg-type]
    users = result.all()

    return UsersPublic(data=list(users), count=count)  # type: ignore


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> Any:
    """Get current user."""
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> Any:
    """Get a specific user by id."""
    user = await session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID) -> Message:
    """Delete a user."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(status_code=403, detail="Super users are not allowed to delete themselves")
    await session.delete(user)
    await session.commit()
    return Message(message="User deleted successfully")
