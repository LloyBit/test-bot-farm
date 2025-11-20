import json
from typing import Optional, Any
import redis.asyncio as async_redis


class CacheRepository:
    """Репозиторий для работы с Redis кэшем."""

    def __init__(self, redis_client: async_redis.Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> Optional[str]:
        """Получение значения из кэша."""
        return await self.redis_client.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Установка значения в кэш."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis_client.set(key, value, ex=ttl)

    async def delete(self, key: str):
        """Удаление ключа из кэша."""
        await self.redis_client.delete(key)

    async def delete_pattern(self, pattern: str):
        """Удаление всех ключей, соответствующих шаблону."""
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)
    
    def make_key(self, *parts: str) -> str:
        """Сборка ключа из частей."""
        return ":".join(parts)

            

