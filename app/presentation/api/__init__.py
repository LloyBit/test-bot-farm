"""Модуль для объединения всех роутов."""
from fastapi import APIRouter

from app.config import get_settings

settings = get_settings()

router = APIRouter()


@router.get("/")
async def root():
    return {"message": settings.project_name, "version": "0.1.0", "docs": "/docs"}


