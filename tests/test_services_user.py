"""Тесты для сервиса пользователей."""
from datetime import datetime
from uuid import uuid4
import pytest

from app.application.models import UserRead
from app.application.services.user import UserService
from app.infrastructure.db.repository.user import UserNotFoundError
from fastapi import HTTPException, status


class TestUserService:
    """Тесты для UserService."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_user_repository, test_user_create):
        """Тест успешного создания пользователя."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        
        # Мокаем репозиторий
        created_data = {
            **test_user_create.model_dump(),
            "locktime": 0,
            "created_at": datetime.now()
        }
        
        async def mock_create_user(data):
            return created_data
        
        mock_user_repository.create_user = AsyncMock(side_effect=mock_create_user)
        
        result = await service.create_user(test_user_create)
        
        assert isinstance(result, UserRead)
        assert result.login == test_user_create.login
        assert result.locktime == 0
        assert result.created_at is not None
        # Проверяем, что locktime и created_at установлены автоматически
        call_args = mock_user_repository.create_user.call_args[0][0]
        assert call_args.get("locktime") == 0
        assert call_args.get("created_at") is not None

    @pytest.mark.asyncio
    async def test_create_user_sets_defaults(self, mock_user_repository, test_user_create):
        """Тест, что locktime и created_at устанавливаются автоматически."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        
        captured_data = {}
        
        async def mock_create_user(data):
            captured_data.update(data)
            return {**data, "created_at": datetime.now()}
        
        mock_user_repository.create_user = AsyncMock(side_effect=mock_create_user)
        
        await service.create_user(test_user_create)
        
        # Проверяем, что locktime и created_at были добавлены
        call_args = mock_user_repository.create_user.call_args[0][0]
        assert "locktime" in call_args
        assert call_args["locktime"] == 0
        assert "created_at" in call_args
        assert isinstance(call_args["created_at"], datetime)

    @pytest.mark.asyncio
    async def test_get_users_empty(self, mock_user_repository):
        """Тест получения пустого списка пользователей."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        
        async def mock_list_users():
            return []
        
        mock_user_repository.list_users = AsyncMock(side_effect=mock_list_users)
        
        result = await service.get_users()
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_users_success(self, mock_user_repository, test_user_read):
        """Тест успешного получения списка пользователей."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        
        async def mock_list_users():
            return [test_user_read.model_dump()]
        
        mock_user_repository.list_users = AsyncMock(side_effect=mock_list_users)
        
        result = await service.get_users()
        
        assert len(result) == 1
        assert isinstance(result[0], UserRead)
        assert result[0].login == test_user_read.login

    @pytest.mark.asyncio
    async def test_acquire_lock_success(self, mock_user_repository, test_user_read):
        """Тест успешной блокировки пользователя."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        user_id = test_user_read.id
        
        async def mock_acquire_lock(uid):
            locked_user = {**test_user_read.model_dump(), "locktime": 1234567890}
            return locked_user, False
        
        mock_user_repository.acquire_lock = AsyncMock(side_effect=mock_acquire_lock)
        
        result = await service.acquire_lock(user_id)
        
        assert result.already_locked is False
        assert isinstance(result.user, UserRead)

    @pytest.mark.asyncio
    async def test_acquire_lock_already_locked(self, mock_user_repository, test_user_read):
        """Тест блокировки уже заблокированного пользователя."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        user_id = test_user_read.id
        
        async def mock_acquire_lock(uid):
            locked_user = {**test_user_read.model_dump(), "locktime": 1234567890}
            return locked_user, True
        
        mock_user_repository.acquire_lock = AsyncMock(side_effect=mock_acquire_lock)
        
        result = await service.acquire_lock(user_id)
        
        assert result.already_locked is True
        assert result.user.locktime != 0

    @pytest.mark.asyncio
    async def test_acquire_lock_user_not_found(self, mock_user_repository):
        """Тест блокировки несуществующего пользователя."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        user_id = uuid4()
        
        async def mock_acquire_lock(uid):
            raise UserNotFoundError()
        
        mock_user_repository.acquire_lock = AsyncMock(side_effect=mock_acquire_lock)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.acquire_lock(user_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_release_lock_success(self, mock_user_repository, test_user_read):
        """Тест успешной разблокировки пользователя."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        user_id = test_user_read.id
        
        async def mock_release_lock(uid):
            unlocked_user = {**test_user_read.model_dump(), "locktime": 0}
            return unlocked_user, False
        
        mock_user_repository.release_lock = AsyncMock(side_effect=mock_release_lock)
        
        result = await service.release_lock(user_id)
        
        assert result.already_unlocked is False
        assert result.user.locktime == 0

    @pytest.mark.asyncio
    async def test_release_lock_already_unlocked(self, mock_user_repository, test_user_read):
        """Тест разблокировки уже разблокированного пользователя."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        user_id = test_user_read.id
        
        async def mock_release_lock(uid):
            return {**test_user_read.model_dump(), "locktime": 0}, True
        
        mock_user_repository.release_lock = AsyncMock(side_effect=mock_release_lock)
        
        result = await service.release_lock(user_id)
        
        assert result.already_unlocked is True
        assert result.user.locktime == 0

    @pytest.mark.asyncio
    async def test_release_lock_user_not_found(self, mock_user_repository):
        """Тест разблокировки несуществующего пользователя."""
        from unittest.mock import AsyncMock
        service = UserService(mock_user_repository)
        user_id = uuid4()
        
        async def mock_release_lock(uid):
            raise UserNotFoundError()
        
        mock_user_repository.release_lock = AsyncMock(side_effect=mock_release_lock)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.release_lock(user_id)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_user_to_read_static_method(self, test_user_read):
        """Тест статического метода _user_to_read."""
        user_dict = test_user_read.model_dump()
        result = UserService._user_to_read(user_dict)
        
        assert isinstance(result, UserRead)
        assert result.id == test_user_read.id
        assert result.login == test_user_read.login

