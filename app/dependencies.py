from fastapi import HTTPException, Request, status

from app.application.container import ServicesContainer

def get_services(request: Request) -> ServicesContainer:
    """Геттер контейнера сервисов из app.state."""
    if not hasattr(request.app.state, 'service_container'):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ServicesContainer упал"
        )
    return request.app.state.service_container


