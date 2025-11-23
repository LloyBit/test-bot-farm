"""Контейнер для сервисов с зависимостями, синглтонами. Ленивая инициализация. property getter для сервисов"""
from app.infrastructure.container import InfrastructureContainer
from app.config import Settings

from app.application.services.user import UserService

class ServicesContainer:
    """Контейнер для бизнес-логики сервисов."""
    
    def __init__(self, settings: Settings, infra: InfrastructureContainer):
        self._settings = settings
        self._infra = infra
        self._user_service: UserService | None = None

    @property
    def user_service(self) -> UserService:
        """Получить user service."""
        if self._user_service is None:
            self._user_service = UserService(user_repo=self._infra.user_repository)
        return self._user_service