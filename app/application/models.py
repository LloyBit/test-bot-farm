"""Модели данных для слоя приложения."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Env(str, Enum):
    """Окружение пользователя."""
    prod = "prod"
    preprod = "preprod"
    stage = "stage"


class Domain(str, Enum):
    """Домен пользователя."""
    canary = "canary"
    regular = "regular"


class UserCreate(BaseModel):
    """Схема создания пользователя."""
    id: UUID = Field(default_factory=uuid4)
    login: EmailStr
    password: str
    project_id: UUID
    env: Env
    domain: Domain


class UserRead(BaseModel):
    """Схема чтения пользователя."""
    id: UUID
    created_at: datetime
    login: EmailStr
    password: str
    project_id: UUID
    env: Env
    domain: Domain
    locktime: int

@dataclass
class LockOperationResult:
    """Результат операции блокировки пользователя."""
    user: UserRead
    already_locked: bool


@dataclass
class UnlockOperationResult:
    """Результат операции разблокировки пользователя."""
    user: UserRead
    already_unlocked: bool