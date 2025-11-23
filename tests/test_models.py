"""Тесты для моделей и схем."""
from datetime import datetime
from uuid import uuid4
import pytest

from app.application.models import Env, Domain, UserCreate, UserRead, LockOperationResult, UnlockOperationResult
from app.presentation.schemas import UserCreate as PresentationUserCreate, UserRead as PresentationUserRead


class TestModels:
    """Тесты для моделей приложения."""

    def test_user_create_validation(self):
        """Тест валидации UserCreate."""
        user = UserCreate(
            login="test@example.com",
            password="password",
            project_id=uuid4(),
            env=Env.prod,
            domain=Domain.regular
        )
        
        assert user.login == "test@example.com"
        assert user.env == Env.prod
        assert user.domain == Domain.regular

    def test_user_create_email_validation(self):
        """Тест валидации email в UserCreate."""
        with pytest.raises(Exception):  # Pydantic validation error
            UserCreate(
                login="not-an-email",
                password="password",
                project_id=uuid4(),
                env=Env.prod,
                domain=Domain.regular
            )

    def test_user_create_defaults(self):
        """Тест значений по умолчанию в UserCreate."""
        user = UserCreate(
            login="test@example.com",
            password="password",
            project_id=uuid4(),
            env=Env.prod,
            domain=Domain.regular
        )
        
        assert user.id is not None
        # locktime и created_at не должны быть в UserCreate
        assert not hasattr(user, "locktime")
        assert not hasattr(user, "created_at")

    def test_user_read_validation(self):
        """Тест валидации UserRead."""
        user = UserRead(
            id=uuid4(),
            created_at=datetime.now(),
            login="test@example.com",
            password="password",
            project_id=uuid4(),
            env=Env.prod,
            domain=Domain.regular,
            locktime=0
        )
        
        assert user.locktime == 0
        assert user.created_at is not None

    def test_lock_operation_result(self, test_user_read):
        """Тест LockOperationResult."""
        result = LockOperationResult(
            user=test_user_read,
            already_locked=False
        )
        
        assert result.user == test_user_read
        assert result.already_locked is False

    def test_unlock_operation_result(self, test_user_read):
        """Тест UnlockOperationResult."""
        result = UnlockOperationResult(
            user=test_user_read,
            already_unlocked=False
        )
        
        assert result.user == test_user_read
        assert result.already_unlocked is False

    def test_env_enum(self):
        """Тест enum Env."""
        assert Env.prod == "prod"
        assert Env.preprod == "preprod"
        assert Env.stage == "stage"

    def test_domain_enum(self):
        """Тест enum Domain."""
        assert Domain.canary == "canary"
        assert Domain.regular == "regular"

    def test_presentation_user_create(self):
        """Тест PresentationUserCreate."""
        user = PresentationUserCreate(
            login="test@example.com",
            password="password",
            project_id=uuid4(),
            env=Env.prod,
            domain=Domain.regular
        )
        
        assert user.login == "test@example.com"
        assert not hasattr(user, "locktime")
        assert not hasattr(user, "created_at")

    def test_presentation_user_read(self):
        """Тест PresentationUserRead."""
        user = PresentationUserRead(
            id=uuid4(),
            created_at=datetime.now(),
            login="test@example.com",
            password="password",
            project_id=uuid4(),
            env=Env.prod,
            domain=Domain.regular,
            locktime=0
        )
        
        assert user.locktime == 0
        assert user.created_at is not None

