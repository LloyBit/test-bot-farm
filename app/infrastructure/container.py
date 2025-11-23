"""Контейнер инфраструктурных компонентов."""
from app.infrastructure.db.database import AsyncDatabaseHelper
from app.config import Settings
from app.infrastructure.db.repository.user import UserRepository

class InfrastructureContainer:
    """Контейнер для инфраструктурных компонентов."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._async_db_helper: AsyncDatabaseHelper | None = None
        self._user_repository: UserRepository | None = None

    @property
    def db_helper(self) -> AsyncDatabaseHelper:
        """Получить database helper."""
        if self._async_db_helper is None:
            self._async_db_helper = AsyncDatabaseHelper(self._settings.database_url)
        return self._async_db_helper

    @property
    def user_repository(self) -> UserRepository:
        """Получить user repository."""
        if self._user_repository is None:
            self._user_repository = UserRepository(self.db_helper)
        return self._user_repository