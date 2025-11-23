"""Тесты для database helper."""
import pytest

from app.infrastructure.db.database import AsyncDatabaseHelper


class TestAsyncDatabaseHelper:
    """Тесты для AsyncDatabaseHelper."""

    def test_init(self):
        """Тест инициализации."""
        url = "postgresql+asyncpg://user:pass@localhost/db"
        helper = AsyncDatabaseHelper(url)
        
        assert helper.database_url == "postgresql+asyncpg://user:pass@localhost/db"
        assert helper.engine is None
        assert helper.async_session_factory is None

    def test_init_with_postgresql(self):
        """Тест инициализации с postgresql:// (должен заменить на postgresql+asyncpg://)."""
        url = "postgresql://user:pass@localhost/db"
        helper = AsyncDatabaseHelper(url)
        
        assert helper.database_url == "postgresql+asyncpg://user:pass@localhost/db"

    @pytest.mark.asyncio
    async def test_connect(self, mock_db_helper):
        """Тест подключения."""
        # mock_db_helper уже подключен в фикстуре
        assert mock_db_helper.engine is not None
        assert mock_db_helper.async_session_factory is not None

    @pytest.mark.asyncio
    async def test_connect_idempotent(self, mock_db_helper):
        """Тест что connect можно вызывать несколько раз."""
        original_engine = mock_db_helper.engine
        await mock_db_helper.connect()
        
        # Должен быть тот же engine
        assert mock_db_helper.engine is original_engine

    @pytest.mark.asyncio
    async def test_session_only(self, mock_db_helper):
        """Тест session_only контекстного менеджера."""
        async with mock_db_helper.session_only() as session:
            assert session is not None

    @pytest.mark.asyncio
    async def test_transaction(self, mock_db_helper):
        """Тест transaction контекстного менеджера."""
        async with mock_db_helper.transaction() as session:
            assert session is not None

    @pytest.mark.asyncio
    async def test_close(self, mock_db_helper):
        """Тест закрытия соединения."""
        engine = mock_db_helper.engine
        assert engine is not None
        
        await mock_db_helper.close()
        
        assert mock_db_helper.engine is None
        assert mock_db_helper.async_session_factory is None

