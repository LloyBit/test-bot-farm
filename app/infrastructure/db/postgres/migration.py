"""Модуль для миграций Alembic."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.config import get_settings

Base = declarative_base()

# Только для миграций можно использовать sync engine
settings = get_settings()
DATABASE_URL = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
engine = create_engine(DATABASE_URL)

