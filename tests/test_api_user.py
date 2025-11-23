"""Тесты для API endpoints пользователей."""
from uuid import uuid4

import pytest
from fastapi import status


class TestUserAPI:
    """Тесты для API endpoints пользователей."""

    def test_create_user_validation_error(self, client):
        """Тест валидации при создании пользователя."""
        invalid_data = {
            "login": "not-an-email",  # Невалидный email
            "password": "test",
            "project_id": str(uuid4()),
            "env": "prod",
            "domain": "regular"
        }
        
        response = client.post("/user/create_user", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

