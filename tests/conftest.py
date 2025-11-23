"""Общие фикстуры для тестов."""
from datetime import datetime
from typing import AsyncGenerator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.container import ServicesContainer
from app.application.models import Env, Domain, UserCreate, UserRead
from app.config import Settings
from app.infrastructure.container import InfrastructureContainer
from app.infrastructure.db.database import AsyncDatabaseHelper
from app.infrastructure.db.repository.user import UserRepository
from app.main import app

@pytest.fixture
def test_settings() -> Settings:
    """Настройки для тестов."""
    return Settings(
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
        debug=True,
        app_name="Test BotFarm Service"
    )


@pytest.fixture
async def mock_db_helper() -> AsyncGenerator[AsyncDatabaseHelper, None]:
    """Мок для AsyncDatabaseHelper."""
    # Используем in-memory SQLite для тестов
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.infrastructure.db.database import AsyncDatabaseHelper
    
    test_db_url = "sqlite+aiosqlite:///:memory:"
    helper = AsyncDatabaseHelper(test_db_url)
    helper.database_url = test_db_url
    
    # Создаем engine напрямую для SQLite
    helper.engine = create_async_engine(
        test_db_url,
        echo=False,
        pool_pre_ping=True,
    )
    helper.async_session_factory = async_sessionmaker(
        helper.engine,
        expire_on_commit=False,
    )
    
    yield helper
    await helper.close()


@pytest.fixture
def mock_user_repository(mock_db_helper) -> UserRepository:
    """Мок для UserRepository."""
    return UserRepository(mock_db_helper)


@pytest.fixture
def mock_user_service(mock_user_repository: UserRepository):
    """Мок для UserService."""
    from app.application.services.user import UserService
    return UserService(mock_user_repository)


@pytest.fixture
def mock_infra_container(test_settings: Settings, mock_db_helper):
    """Мок для InfrastructureContainer."""
    container = InfrastructureContainer(test_settings)
    container._async_db_helper = mock_db_helper
    return container


@pytest.fixture
def mock_services_container(mock_infra_container: InfrastructureContainer, test_settings: Settings):
    """Мок для ServicesContainer."""
    return ServicesContainer(settings=test_settings, infra=mock_infra_container)


@pytest.fixture
def test_user_data() -> dict:
    """Тестовые данные пользователя."""
    return {
        "id": uuid4(),
        "login": "test@example.com",
        "password": "test_password",
        "project_id": uuid4(),
        "env": Env.prod,
        "domain": Domain.regular,
    }


@pytest.fixture
def test_user_create(test_user_data: dict) -> UserCreate:
    """Тестовый UserCreate."""
    return UserCreate(**test_user_data)


@pytest.fixture
def test_user_read(test_user_data: dict) -> UserRead:
    """Тестовый UserRead."""
    return UserRead(
        **test_user_data,
        created_at=datetime.now(),
        locktime=0
    )


@pytest.fixture
def client(mock_services_container: ServicesContainer) -> TestClient:
    """Тестовый клиент FastAPI."""
    # Сохраняем оригинальный app.state
    original_state = getattr(app.state, "service_container", None)
    original_infra = getattr(app.state, "infra", None)
    
    # Устанавливаем моки
    app.state.service_container = mock_services_container
    app.state.infra = mock_services_container._infra
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Восстанавливаем оригинальное состояние
        if original_state is not None:
            app.state.service_container = original_state
        elif hasattr(app.state, "service_container"):
            delattr(app.state, "service_container")
        if original_infra is not None:
            app.state.infra = original_infra
        elif hasattr(app.state, "infra"):
            delattr(app.state, "infra")


@pytest.fixture
async def db_session(mock_db_helper: AsyncDatabaseHelper) -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД для тестов."""
    async with mock_db_helper.session_only() as session:
        yield session

