from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status

from app.application.models import LockOperationResult, UnlockOperationResult, UserCreate, UserRead
from app.infrastructure.db.repository.user import UserNotFoundError, UserRepository


class UserService:
    """Бизнес логика для операций с пользователями."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def create_user(self, user: UserCreate) -> UserRead:
        user_data = user.model_dump()
        # Автоматически устанавливаем locktime и created_at в сервисе
        user_data["locktime"] = 0
        user_data["created_at"] = datetime.now()
        created = await self._user_repo.create_user(user_data)
        return self._user_to_read(created)

    async def get_users(self) -> list[UserRead]:
        users = await self._user_repo.list_users()
        return [self._user_to_read(u) for u in users]

    async def acquire_lock(self, user_id: UUID) -> LockOperationResult:
        try:
            user, already_locked = await self._user_repo.acquire_lock(user_id)
        except UserNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return LockOperationResult(user=self._user_to_read(user), already_locked=already_locked)

    async def release_lock(self, user_id: UUID) -> UnlockOperationResult:
        try:
            user, already_unlocked = await self._user_repo.release_lock(user_id)
        except UserNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UnlockOperationResult(user=self._user_to_read(user), already_unlocked=already_unlocked)

    @staticmethod
    def _user_to_read(data: dict) -> UserRead:
        return UserRead.model_validate(data)
