from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Настройки приложения."""
    
    # База данных
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/botfarm"

    # Приложение
    debug: bool = False
    app_name: str = "BotFarm Service"
    project_name: str = "BotFarm"
    api_v1_prefix: str = "/api/v1"

    # Логирование
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_log_level: str = "WARNING"
    file_log_level: str = "DEBUG"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


def get_settings() -> Settings:
    """Получить настройки приложения."""
    return Settings()

