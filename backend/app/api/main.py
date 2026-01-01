from fastapi import APIRouter

from app.api.routes import (
    device_types,
    devices,
    login,
    monitoring,
    picture_display,
    private,
    rooms,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(devices.router)
api_router.include_router(rooms.router)
api_router.include_router(device_types.router)
api_router.include_router(picture_display.router)
api_router.include_router(monitoring.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
