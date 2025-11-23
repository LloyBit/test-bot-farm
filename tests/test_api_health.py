"""Тесты для health check endpoints."""
import pytest
from fastapi import status
from unittest.mock import Mock


class TestHealthAPI:
    """Тесты для health check endpoints."""

    def test_liveness_success(self, client):
        """Тест успешной проверки жизнеспособности."""
        response = client.get("/health/liveness")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Жив"
        assert "успешно" in data["message"]

    def test_startup_success(self, client, mock_infra_container):
        """Тест успешной проверки запуска."""
        # Убеждаемся, что инфраструктура инициализирована и engine существует
        # mock_infra_container уже имеет mock_db_helper с engine
        
        response = client.get("/health/startup")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "successful" in data["message"]

    def test_startup_infra_not_initialized(self, client):
        """Тест проверки запуска без инициализированной инфраструктуры."""
        # Сохраняем оригинальное состояние
        original_infra = getattr(client.app.state, "infra", None)
        
        # Удаляем infra из app.state
        if hasattr(client.app.state, "infra"):
            delattr(client.app.state, "infra")
        
        try:
            response = client.get("/health/startup")
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            data = response.json()
            assert "not initialized" in data["detail"]
        finally:
            # Восстанавливаем
            if original_infra is not None:
                client.app.state.infra = original_infra

    def test_readiness_infra_not_initialized(self, client):
        """Тест проверки готовности без инициализированной инфраструктуры."""
        # Сохраняем оригинальное состояние
        original_infra = getattr(client.app.state, "infra", None)
        
        # Удаляем infra из app.state
        if hasattr(client.app.state, "infra"):
            delattr(client.app.state, "infra")
        
        try:
            response = client.get("/health/readiness")
            
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            data = response.json()
            assert "not initialized" in data["detail"]
        finally:
            # Восстанавливаем
            if original_infra is not None:
                client.app.state.infra = original_infra

