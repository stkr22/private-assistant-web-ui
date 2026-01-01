"""API routes for Room management."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from private_assistant_commons.database.models import Room
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.models_commons_api import RoomCreate, RoomPublic, RoomsPublic, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=RoomsPublic)
async def read_rooms(session: SessionDep, _current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve rooms with pagination."""
    count_statement = select(func.count()).select_from(Room)
    result = await session.exec(count_statement)
    count = result.one()

    statement = select(Room).offset(skip).limit(limit)
    result = await session.exec(statement)  # type: ignore[arg-type]
    rooms = result.all()

    return RoomsPublic(data=list(rooms), count=count)  # type: ignore[arg-type]


@router.get("/{room_id}", response_model=RoomPublic)
async def read_room(session: SessionDep, _current_user: CurrentUser, room_id: uuid.UUID) -> Any:
    """Get room by ID."""
    room = await session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/", response_model=RoomPublic)
async def create_room(*, session: SessionDep, _current_user: CurrentUser, room_in: RoomCreate) -> Any:
    """Create new room."""
    room = Room.model_validate(room_in)
    session.add(room)
    await session.commit()
    await session.refresh(room)
    return room


@router.put("/{room_id}", response_model=RoomPublic)
async def update_room(
    *,
    session: SessionDep,
    _current_user: CurrentUser,
    room_id: uuid.UUID,
    room_in: RoomUpdate,
) -> Any:
    """Update a room."""
    room = await session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    update_dict = room_in.model_dump(exclude_unset=True)
    room.sqlmodel_update(update_dict)
    session.add(room)
    await session.commit()
    await session.refresh(room)
    return room


@router.delete("/{room_id}")
async def delete_room(session: SessionDep, _current_user: CurrentUser, room_id: uuid.UUID) -> Message:
    """Delete a room."""
    room = await session.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    await session.delete(room)
    await session.commit()
    return Message(message="Room deleted successfully")
