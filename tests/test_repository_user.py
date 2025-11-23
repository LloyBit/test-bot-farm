"""Тесты для репозитория пользователей."""
from datetime import datetime
from uuid import uuid4
import pytest

from app.application.models import Env, Domain
from app.infrastructure.db.repository.user import UserRepository, UserNotFoundError
from app.infrastructure.db.schemas import User as UserORM


class TestUserRepository:
    """Тесты для UserRepository."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db_helper, test_user_data):
        """Тест успешного создания пользователя."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу для тестов
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        user_data = {
            **test_user_data,
            "locktime": 0,
            "created_at": datetime.now()
        }
        
        result = await repository.create_user(user_data)
        
        assert result["id"] == user_data["id"]
        assert result["login"] == user_data["login"]
        assert result["locktime"] == 0

    @pytest.mark.asyncio
    async def test_list_users_empty(self, mock_db_helper):
        """Тест получения пустого списка пользователей."""
        repository = UserRepository(mock_db_helper)
        
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        result = await repository.list_users()
        
        assert result == []

    @pytest.mark.asyncio
    async def test_list_users_success(self, mock_db_helper, test_user_data):
        """Тест успешного получения списка пользователей."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        # Создаем пользователя
        user_data = {
            **test_user_data,
            "locktime": 0,
            "created_at": datetime.now()
        }
        await repository.create_user(user_data)
        
        # Получаем список
        result = await repository.list_users()
        
        assert len(result) == 1
        assert result[0]["login"] == user_data["login"]

    @pytest.mark.asyncio
    async def test_acquire_lock_success(self, mock_db_helper, test_user_data):
        """Тест успешной блокировки пользователя."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        # Создаем пользователя
        user_data = {
            **test_user_data,
            "locktime": 0,
            "created_at": datetime.now()
        }
        await repository.create_user(user_data)
        
        # Блокируем
        user_dict, already_locked = await repository.acquire_lock(user_data["id"])
        
        assert already_locked is False
        assert user_dict["locktime"] != 0

    @pytest.mark.asyncio
    async def test_acquire_lock_already_locked(self, mock_db_helper, test_user_data):
        """Тест блокировки уже заблокированного пользователя."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        # Создаем пользователя
        user_data = {
            **test_user_data,
            "locktime": 1234567890,
            "created_at": datetime.now()
        }
        await repository.create_user(user_data)
        
        # Пытаемся заблокировать снова
        user_dict, already_locked = await repository.acquire_lock(user_data["id"])
        
        assert already_locked is True
        assert user_dict["locktime"] == 1234567890

    @pytest.mark.asyncio
    async def test_acquire_lock_user_not_found(self, mock_db_helper):
        """Тест блокировки несуществующего пользователя."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        with pytest.raises(UserNotFoundError):
            await repository.acquire_lock(uuid4())

    @pytest.mark.asyncio
    async def test_release_lock_success(self, mock_db_helper, test_user_data):
        """Тест успешной разблокировки пользователя."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        # Создаем заблокированного пользователя
        user_data = {
            **test_user_data,
            "locktime": 1234567890,
            "created_at": datetime.now()
        }
        await repository.create_user(user_data)
        
        # Разблокируем
        user_dict, already_unlocked = await repository.release_lock(user_data["id"])
        
        assert already_unlocked is False
        assert user_dict["locktime"] == 0

    @pytest.mark.asyncio
    async def test_release_lock_already_unlocked(self, mock_db_helper, test_user_data):
        """Тест разблокировки уже разблокированного пользователя."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        # Создаем разблокированного пользователя
        user_data = {
            **test_user_data,
            "locktime": 0,
            "created_at": datetime.now()
        }
        await repository.create_user(user_data)
        
        # Пытаемся разблокировать снова
        user_dict, already_unlocked = await repository.release_lock(user_data["id"])
        
        assert already_unlocked is True
        assert user_dict["locktime"] == 0

    @pytest.mark.asyncio
    async def test_release_lock_user_not_found(self, mock_db_helper):
        """Тест разблокировки несуществующего пользователя."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем таблицу
        async with mock_db_helper.engine.begin() as conn:
            await conn.run_sync(UserORM.metadata.create_all)
        
        with pytest.raises(UserNotFoundError):
            await repository.release_lock(uuid4())

    def test_to_dict(self, mock_db_helper):
        """Тест метода _to_dict."""
        repository = UserRepository(mock_db_helper)
        
        # Создаем тестовый объект UserORM
        user_orm = UserORM(
            id=uuid4(),
            login="test@example.com",
            password="password",
            project_id=uuid4(),
            env=Env.prod,
            domain=Domain.regular,
            locktime=0,
            created_at=datetime.now()
        )
        
        result = repository._to_dict(user_orm)
        
        assert result["id"] == user_orm.id
        assert result["login"] == user_orm.login
        assert result["locktime"] == user_orm.locktime

