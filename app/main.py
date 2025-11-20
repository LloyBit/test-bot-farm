"""Точка входа в основное приложение."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.presentation.api import router as all_routers
from app.presentation.middleware import ExceptionMiddleware, LoggingMiddleware
from app.application.container import ServicesContainer
from app.infrastructure.container import InfrastructureContainer
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик событий жизненного цикла FastAPI."""
    # Startup

    # Создаем контейнер репозиториев
    app.state.infra = InfrastructureContainer(settings=settings)
    await app.state.infra.db_helper.connect()
    await app.state.infra.redis_client.ping()  # Проверяем подключение к Redis

    # Билдим образ контейнера сервисов
    app.state.service_container = ServicesContainer(settings=settings, infra=app.state.infra)

    yield

    # Shutdown

    # Закрываем соединения
    await app.state.infra.db_helper.close()
    await app.state.infra.redis_client.close()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# Добавляем middleware. Порядок важен: ExceptionMiddleware должен быть первым
app.add_middleware(ExceptionMiddleware, debug=settings.debug)
app.add_middleware(LoggingMiddleware, log_level=settings.log_level)

# Подключаем предварительно собранные роуты
app.include_router(all_routers)
