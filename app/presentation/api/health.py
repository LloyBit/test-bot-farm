from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import text

router = APIRouter()


@router.get("/startup")
async def startup(request: Request) -> dict[str, str]:
    """Проверка запуска приложения"""
    try:
        # Проверяем, что инфраструктура инициализирована
        if not hasattr(request.app.state, "infra"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Infrastructure not initialized"
            )
        
        infra = request.app.state.infra
        if infra.db_helper.engine is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not connected"
            )
        
        return {"status": "healthy", "message": "Startup successful"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Startup check failed: {str(e)}"
        )


@router.get("/liveness")
async def liveness() -> dict[str, str]:
    """Проверка жизнеспособности приложения"""
    return {"status": "Жив", "message": "Проверка жизнеспособности приложения прошла успешно"}


@router.get("/readiness")
async def readiness(request: Request) -> dict[str, str]:
    """Проверка готовности приложения принимать трафик"""
    try:
        # Проверяем, что инфраструктура инициализирована
        if not hasattr(request.app.state, "infra"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Infrastructure not initialized"
            )
        
        infra = request.app.state.infra
        db_helper = infra.db_helper
        
        # Проверяем подключение к БД через простой запрос
        if db_helper.engine is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not connected"
            )
        
        # Выполняем простой запрос для проверки доступности БД
        async with db_helper.session_only() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        
        return {"status": "ready", "message": "Readiness check successful"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Проверка готовности приложения прошла с ошибкой: {str(e)}"
        )
