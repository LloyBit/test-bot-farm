from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.container import ServicesContainer
from app.dependencies import get_services
from app.presentation.schemas import LockResponse, UnlockResponse, UserCreate, UserRead

router = APIRouter()


@router.post("/create_user", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, services: ServicesContainer = Depends(get_services)) -> UserRead:
    return await services.user_service.create_user(user)


@router.get("/get_users", response_model=list[UserRead], status_code=status.HTTP_200_OK)
async def get_users(services: ServicesContainer = Depends(get_services)) -> list[UserRead]:
    return await services.user_service.get_users()


@router.post("/acquire_lock", response_model=LockResponse, status_code=status.HTTP_200_OK)
async def acquire_lock(user_id: UUID, services: ServicesContainer = Depends(get_services)) -> LockResponse:
    operation = await services.user_service.acquire_lock(user_id)
    if operation.already_locked:
        return LockResponse(message="Данный юзер уже был заблокирован")
    return LockResponse(message=f"Юзер {user_id} заблокирован", locktime=operation.user.locktime)


@router.post("/release_lock", response_model=UnlockResponse, status_code=status.HTTP_200_OK)
async def release_lock(user_id: UUID, services: ServicesContainer = Depends(get_services)) -> UnlockResponse:
    operation = await services.user_service.release_lock(user_id)
    if operation.already_unlocked:
        return UnlockResponse(message="Данный юзер уже был разблокирован", locktime=operation.user.locktime)
    return UnlockResponse(message=f"Юзер {operation.user.id} разблокирован", locktime=operation.user.locktime)