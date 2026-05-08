"""
Этот файл отвечает за подключение к базе данных.

SQLAlchemy использует три основных компонента:

engine — соединение с базой
session — сессия для выполнения запросов
Base — базовый класс для моделей таблиц
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings


# создаём engine (соединение с БД)
engine = create_engine(settings.DATABASE_URL)


# фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# базовый класс для всех моделей
Base = declarative_base()



"""
Dependency для FastAPI.

Каждый HTTP запрос получает свою сессию БД.
После завершения запроса сессия автоматически закрывается.
"""
def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()