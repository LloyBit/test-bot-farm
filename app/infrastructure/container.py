"""Контейнер инфраструктурных компонентов."""
import redis.asyncio as async_redis

from app.infrastructure.db.postgres.database import AsyncDatabaseHelper
from app.infrastructure.db.redis.repositories import CacheRepository
from app.config import Settings


class InfrastructureContainer:
    """Контейнер для инфраструктурных компонентов."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._async_db_helper: AsyncDatabaseHelper | None = None
        self._async_redis_helper: async_redis.Redis | None = None
        self._cache_repo: CacheRepository | None = None

    @property
    def redis_client(self) -> async_redis.Redis:
        """Получить Redis клиент."""
        if self._async_redis_helper is None:
            self._async_redis_helper = async_redis.from_url(
                self._settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10,
                retry_on_timeout=True,
                socket_keepalive=True,
            )
        return self._async_redis_helper

    @property
    def db_helper(self) -> AsyncDatabaseHelper:
        """Получить database helper."""
        if self._async_db_helper is None:
            self._async_db_helper = AsyncDatabaseHelper(self._settings.database_url)
        return self._async_db_helper

    @property
    def cache_repo(self) -> CacheRepository:
        """Получить cache repository."""
        if self._cache_repo is None:
            self._cache_repo = CacheRepository(self.redis_client)
        return self._cache_repo