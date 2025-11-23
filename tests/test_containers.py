"""Тесты для контейнеров."""
import pytest
from unittest.mock import Mock

from app.application.container import ServicesContainer
from app.infrastructure.container import InfrastructureContainer
from app.config import Settings
from app.application.services.user import UserService


class TestInfrastructureContainer:
    """Тесты для InfrastructureContainer."""

    def test_init(self, test_settings):
        """Тест инициализации контейнера."""
        container = InfrastructureContainer(test_settings)
        assert container._settings == test_settings
        assert container._async_db_helper is None
        assert container._user_repository is None

    def test_db_helper_property(self, test_settings, mock_db_helper):
        """Тест свойства db_helper."""
        container = InfrastructureContainer(test_settings)
        container._async_db_helper = mock_db_helper
        
        result = container.db_helper
        assert result == mock_db_helper

    def test_db_helper_lazy_init(self, test_settings):
        """Тест ленивой инициализации db_helper."""
        container = InfrastructureContainer(test_settings)
        result = container.db_helper
        
        assert result is not None
        assert container._async_db_helper is not None

    def test_user_repository_property(self, test_settings, mock_db_helper):
        """Тест свойства user_repository."""
        container = InfrastructureContainer(test_settings)
        container._async_db_helper = mock_db_helper
        
        result = container.user_repository
        assert result is not None
        assert container._user_repository is not None

    def test_user_repository_lazy_init(self, test_settings, mock_db_helper):
        """Тест ленивой инициализации user_repository."""
        container = InfrastructureContainer(test_settings)
        container._async_db_helper = mock_db_helper
        
        repo1 = container.user_repository
        repo2 = container.user_repository
        
        # Должен быть тот же объект (singleton)
        assert repo1 is repo2


class TestServicesContainer:
    """Тесты для ServicesContainer."""

    def test_init(self, test_settings, mock_infra_container):
        """Тест инициализации контейнера."""
        container = ServicesContainer(test_settings, mock_infra_container)
        assert container._settings == test_settings
        assert container._infra == mock_infra_container
        assert container._user_service is None

    def test_user_service_property(self, test_settings, mock_infra_container):
        """Тест свойства user_service."""
        container = ServicesContainer(test_settings, mock_infra_container)
        
        result = container.user_service
        assert result is not None
        assert isinstance(result, UserService)
        assert container._user_service is not None

    def test_user_service_lazy_init(self, test_settings, mock_infra_container):
        """Тест ленивой инициализации user_service."""
        container = ServicesContainer(test_settings, mock_infra_container)
        
        service1 = container.user_service
        service2 = container.user_service
        
        # Должен быть тот же объект (singleton)
        assert service1 is service2

