"""Модуль для объединения всех роутов."""
from fastapi import APIRouter

from app.presentation.api.user import router as user_router
from app.presentation.api.health import router as health_router

router = APIRouter()

router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(health_router, prefix="/health", tags=["health"])


