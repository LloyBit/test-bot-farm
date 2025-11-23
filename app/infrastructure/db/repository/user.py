from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.infrastructure.db.database import AsyncDatabaseHelper
from app.infrastructure.db.schemas import User as UserORM

class UserRepositoryError(Exception):
    """Базовая ошибка репозитория."""


class UserNotFoundError(UserRepositoryError):
    """Пользователь не найден."""


class UserRepository:
    """Простая обертка над запросами к таблице пользователей."""

    def __init__(self, db_helper: AsyncDatabaseHelper) -> None:
        self._db_helper = db_helper

    async def create_user(self, user_data: dict) -> dict:
        """Создать пользователя."""
        async with self._db_helper.transaction() as session:
            user = UserORM(**user_data)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return self._to_dict(user)

    async def list_users(self) -> list[dict]:
        """Получить всех пользователей."""
        async with self._db_helper.session_only() as session:
            result = await session.execute(select(UserORM))
            return [self._to_dict(user) for user in result.scalars().all()]

    async def acquire_lock(self, user_id: UUID) -> tuple[dict, bool]:
        """Заблокировать пользователя"""
        async with self._db_helper.transaction() as session:
            stmt = select(UserORM).where(UserORM.id == user_id).with_for_update()
            user = (await session.execute(stmt)).scalar_one_or_none()
            if not user:
                raise UserNotFoundError()

            already_locked = user.locktime != 0
            if not already_locked:
                user.locktime = int(datetime.now(timezone.utc).timestamp())
                session.add(user)

            return self._to_dict(user), already_locked


    async def release_lock(self, user_id: UUID) -> tuple[dict, bool]:
        """Разблокировать пользователя."""
        async with self._db_helper.transaction() as session:
            stmt = select(UserORM).where(UserORM.id == user_id).with_for_update()
            user = (await session.execute(stmt)).scalar_one_or_none()
            if not user:
                raise UserNotFoundError()

            already_unlocked = user.locktime == 0
            if not already_unlocked:
                user.locktime = 0
                session.add(user)

            return self._to_dict(user), already_unlocked

    def _to_dict(self, user: UserORM) -> dict:
        """Маппер UserORM в словарь."""
        return {
            "id": user.id,
            "created_at": user.created_at,
            "login": user.login,
            "password": user.password,
            "project_id": user.project_id,
            "env": user.env,
            "domain": user.domain,
            "locktime": user.locktime,
        }