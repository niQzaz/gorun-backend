"""
Этот файл отвечает за конфигурацию проекта.

Здесь хранятся:
- строка подключения к базе
- секретный ключ
- другие настройки приложения

Используем BaseSettings из Pydantic.
Он автоматически может читать переменные из .env файла.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # строка подключения к PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/appdb"

    # секретный ключ для JWT
    SECRET_KEY: str = "reallySecretKey"

    # алгоритм подписи JWT
    ALGORITHM: str = "HS256"

    # время жизни токена
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"


# создаём глобальный объект настроек
settings = Settings()