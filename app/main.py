from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.database import Base, engine
from app.models import conversations, friend, friend_request, joint_run, joint_run_route_point, message, user, user_run
from app.routers.auth_router import router as auth_router
from app.routers.chat_router import router as chat_router
from app.routers.chat_ws import router as chat_ws_router
from app.routers.friend_router import router as friend_router
from app.routers.run_router import router as run_router
from app.routers.user_router import router as user_router
from app.logger import app_logger, db_logger


MEDIA_DIR = Path(__file__).resolve().parent / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

app_logger.info("Запуск приложения GoRun | Starting GoRun application")

app = FastAPI()

app_logger.info("Создание таблиц БД | Creating database tables")
Base.metadata.create_all(bind=engine)


def run_runtime_migrations() -> None:
    db_logger.info("Запуск runtime миграций | Running runtime migrations")
    inspector = inspect(engine)
    if not inspector.has_table("messages"):
        db_logger.warning("Таблица messages не найдена, миграции пропущены | Messages table not found, skipping migrations")
        return

    existing_columns = {column["name"] for column in inspector.get_columns("messages")}
    migrations: list[str] = []

    if "message_type" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN message_type VARCHAR(32) NOT NULL DEFAULT 'text'")
    if "client_message_id" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN client_message_id VARCHAR(64)")
    if "image_url" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN image_url TEXT")
    if "shared_run_code" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN shared_run_code VARCHAR(64)")
    if "shared_run_name" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN shared_run_name VARCHAR(120)")
    if "shared_run_distance_km" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN shared_run_distance_km DOUBLE PRECISION")
    if "shared_run_duration_millis" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN shared_run_duration_millis INTEGER")
    if "shared_run_performed_at" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN shared_run_performed_at TIMESTAMP WITH TIME ZONE")
    if "joint_run_challenge_id" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN joint_run_challenge_id INTEGER")
    if "is_read" not in existing_columns:
        migrations.append("ALTER TABLE messages ADD COLUMN is_read BOOLEAN NOT NULL DEFAULT FALSE")

    # Миграции для joint_run_challenges
    if inspector.has_table("joint_run_challenges"):
        joint_run_columns = {column["name"] for column in inspector.get_columns("joint_run_challenges")}
        if "creator_max_speed_kmh" not in joint_run_columns:
            migrations.append("ALTER TABLE joint_run_challenges ADD COLUMN creator_max_speed_kmh DOUBLE PRECISION")
        if "opponent_max_speed_kmh" not in joint_run_columns:
            migrations.append("ALTER TABLE joint_run_challenges ADD COLUMN opponent_max_speed_kmh DOUBLE PRECISION")

    if not migrations:
        db_logger.info("Миграции не требуются | No migrations needed")
        return

    db_logger.info(f"Применение {len(migrations)} миграций | Applying {len(migrations)} migrations")
    with engine.begin() as connection:
        for migration in migrations:
            db_logger.debug(f"Выполнение миграции | Executing migration: {migration[:50]}...")
            connection.execute(text(migration))

    db_logger.info("Runtime миграции успешно применены | Runtime migrations completed successfully")


run_runtime_migrations()

app_logger.info("Подключение роутеров | Mounting routers")
app.include_router(auth_router)
app.include_router(friend_router)
app.include_router(user_router)
app.include_router(run_router)
app.include_router(chat_router)
app.include_router(chat_ws_router)
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

app_logger.info("Приложение GoRun успешно запущено | GoRun application started successfully")


@app.get("/")
async def root():
    app_logger.debug("Запрос к корневому эндпоинту | Root endpoint accessed")
    return {"message": "Hello World"}
