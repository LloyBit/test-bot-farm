"""Dependencies для FastAPI."""
from fastapi import Request, HTTPException
from app.config import Settings
from app.application.container import ServicesContainer
from app.infrastructure.container import InfrastructureContainer


def get_services(request: Request) -> ServicesContainer:
    """Получить контейнер сервисов из app.state."""
    if not hasattr(request.app.state, 'service_container'):
        raise HTTPException(
            status_code=500,
            detail="ServicesContainer упал. Проверьте lifespan."
        )
    return request.app.state.service_container


def get_infrastructure(request: Request) -> InfrastructureContainer:
    """Получить контейнер инфраструктуры из app.state."""
    if not hasattr(request.app.state, 'infra'):
        raise HTTPException(
            status_code=500,
            detail="InfrastructureContainer упал. Проверьте lifespan."
        )
    return request.app.state.infra

