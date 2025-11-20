"""Контейнер для сервисов с зависимостями, синглтонами. Ленивая инициализация. property getter для сервисов"""
from app.infrastructure.container import InfrastructureContainer
from app.config import Settings


class ServicesContainer:
    """Контейнер для бизнес-логики сервисов."""
    
    def __init__(self, settings: Settings, infra: InfrastructureContainer):
        self._settings = settings
        self._infra = infra
        # Здесь можно добавить ленивую инициализацию сервисов
        # Пример:
        # self._user_service: UserService | None = None
    
    # Пример использования:
    # @property
    # def user_service(self) -> UserService:
    #     """Получить user service."""
    #     if self._user_service is None:
    #         self._user_service = UserService(
    #             user_repo=self._infra.users_pg,
    #             cache_repo=self._infra.cache_repo,
    #             settings=self._settings
    #         )
    #     return self._user_service