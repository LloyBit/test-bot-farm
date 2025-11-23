"""Тесты для dependencies."""
import pytest
from fastapi import HTTPException, Request, status
from unittest.mock import Mock

from app.dependencies import get_services
from app.application.container import ServicesContainer


class TestDependencies:
    """Тесты для dependencies."""

    def test_get_services_success(self):
        """Тест успешного получения сервисов."""
        mock_container = Mock(spec=ServicesContainer)
        mock_request = Mock(spec=Request)
        mock_request.app.state.service_container = mock_container
        
        result = get_services(mock_request)
        
        assert result == mock_container

    def test_get_services_not_initialized(self):
        """Тест получения сервисов когда контейнер не инициализирован."""
        mock_request = Mock(spec=Request)
        mock_request.app.state = Mock()
        delattr(mock_request.app.state, 'service_container')
        mock_request.app.state.__dict__ = {}
        
        with pytest.raises(HTTPException) as exc_info:
            get_services(mock_request)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "упал" in exc_info.value.detail

