from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, selectinload

from app.crud import user_crud
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_run import UserRun, UserRunRoutePoint
from app.routers.user_router import serialize_user
from app.schemas.run_schema import (
    UserRunCreate,
    UserRunResponse,
    UserRunShareResponse,
)
from app.logger import run_logger


router = APIRouter(prefix="/user-runs", tags=["user-runs"])


def serialize_route_point(route_point: UserRunRoutePoint) -> dict:
    return {
        "sequence_index": route_point.sequence_index,
        "latitude": route_point.latitude,
        "longitude": route_point.longitude,
        "elapsed_time_millis": route_point.elapsed_time_millis,
        "distance_meters": route_point.distance_meters,
    }


def serialize_run(request: Request, run: UserRun, owner=None) -> dict:
    return {
        "id": run.id,
        "user_id": run.user_id,
        "name": run.name,
        "performed_at": run.performed_at,
        "duration_millis": run.duration_millis,
        "distance_km": run.distance_km,
        "avg_speed_kmh": run.avg_speed_kmh,
        "max_speed_kmh": run.max_speed_kmh,
        "pace_min_per_km": run.pace_min_per_km,
        "is_shared": run.is_shared,
        "share_code": run.share_code,
        "route_points": [serialize_route_point(point) for point in run.route_points],
        "owner": serialize_user(request, owner) if owner is not None else None,
    }


def get_owned_run(db: Session, run_id: int, owner_id: int) -> UserRun | None:
    return (
        db.query(UserRun)
        .options(selectinload(UserRun.route_points))
        .filter(UserRun.id == run_id, UserRun.user_id == owner_id)
        .first()
    )


def get_existing_run_by_timestamp(db: Session, owner_id: int, performed_at: datetime) -> UserRun | None:
    return (
        db.query(UserRun)
        .options(selectinload(UserRun.route_points))
        .filter(UserRun.user_id == owner_id, UserRun.performed_at == performed_at)
        .first()
    )


@router.post("", response_model=UserRunResponse)
def create_user_run(
    data: UserRunCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    run_logger.info(f"Создание забега | Creating run: user_id={current_user.id}, name={data.name}")

    name = data.name.strip()
    if not name:
        run_logger.warning(f"Создание забега отклонено: пустое имя | Run creation rejected: empty name - user_id={current_user.id}")
        raise HTTPException(status_code=400, detail="Run name cannot be empty")

    performed_at = datetime.fromtimestamp(data.performed_at_millis / 1000.0, tz=timezone.utc)
    run_logger.debug(f"Проверка дубликата забега | Checking for duplicate run: user_id={current_user.id}, performed_at={performed_at}")

    existing_run = get_existing_run_by_timestamp(db, current_user.id, performed_at)
    if existing_run is not None:
        run_logger.info(f"Найден существующий забег | Found existing run: run_id={existing_run.id}, user_id={current_user.id}")
        return serialize_run(request, existing_run)

    run_logger.debug(f"Создание нового забега в БД | Creating new run in database: distance={data.distance_km}km, duration={data.duration_millis}ms")
    run = UserRun(
        user_id=current_user.id,
        name=name,
        performed_at=performed_at,
        duration_millis=data.duration_millis,
        distance_km=data.distance_km,
        avg_speed_kmh=data.avg_speed_kmh,
        max_speed_kmh=data.max_speed_kmh,
        pace_min_per_km=data.pace_min_per_km,
    )

    db.add(run)
    db.flush()

    run_logger.debug(f"Добавление точек маршрута | Adding route points: run_id={run.id}, points_count={len(data.route_points)}")
    for point in data.route_points:
        db.add(UserRunRoutePoint(
            run_id=run.id,
            sequence_index=point.sequence_index,
            latitude=point.latitude,
            longitude=point.longitude,
            elapsed_time_millis=point.elapsed_time_millis,
            distance_meters=point.distance_meters,
        ))

    try:
        db.commit()
        run_logger.info(f"Забег успешно создан | Run successfully created: run_id={run.id}, user_id={current_user.id}, distance={data.distance_km}km")
    except Exception as e:
        db.rollback()
        run_logger.error(f"Ошибка при сохранении забега | Error saving run: user_id={current_user.id}, error={str(e)}")
        raise

    created_run = get_owned_run(db, run.id, current_user.id)
    if created_run is None:
        run_logger.error(f"Забег создан, но не найден при загрузке | Run created but not found on reload: run_id={run.id}")
        raise HTTPException(status_code=500, detail="Run was created but could not be loaded")

    return serialize_run(request, created_run)


@router.get("/me", response_model=list[UserRunResponse])
def get_my_runs(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    run_logger.info(f"Получение списка забегов пользователя | Getting user runs: user_id={current_user.id}, limit={limit}, offset={offset}")

    runs = (
        db.query(UserRun)
        .options(selectinload(UserRun.route_points))
        .filter(UserRun.user_id == current_user.id)
        .order_by(UserRun.performed_at.desc(), UserRun.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    run_logger.info(f"Список забегов получен | Runs list retrieved: user_id={current_user.id}, count={len(runs)}")
    return [serialize_run(request, run) for run in runs]


@router.post("/{run_id}/share", response_model=UserRunShareResponse)
def share_my_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    run_logger.info(f"Публикация забега | Sharing run: run_id={run_id}, user_id={current_user.id}")

    run = get_owned_run(db, run_id, current_user.id)
    if run is None:
        run_logger.warning(f"Забег не найден | Run not found: run_id={run_id}, user_id={current_user.id}")
        raise HTTPException(status_code=404, detail="Run not found")

    if not run.is_shared:
        run_logger.debug(f"Установка флага публикации | Setting shared flag: run_id={run_id}")
        run.is_shared = True
        try:
            db.commit()
            run_logger.info(f"Забег успешно опубликован | Run successfully shared: run_id={run_id}, share_code={run.share_code}")
        except Exception as e:
            db.rollback()
            run_logger.error(f"Ошибка при публикации забега | Error sharing run: run_id={run_id}, error={str(e)}")
            raise
        db.refresh(run)
    else:
        run_logger.debug(f"Забег уже опубликован | Run already shared: run_id={run_id}")

    return {
        "run_id": run.id,
        "is_shared": run.is_shared,
        "share_code": run.share_code,
    }


@router.get("/shared/{share_code}", response_model=UserRunResponse)
def get_shared_run(
    share_code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    run_logger.info(f"Получение опубликованного забега | Getting shared run: share_code={share_code}")

    run = (
        db.query(UserRun)
        .options(selectinload(UserRun.route_points))
        .filter(UserRun.share_code == share_code)
        .first()
    )

    if run is None or not run.is_shared:
        run_logger.warning(f"Опубликованный забег не найден | Shared run not found: share_code={share_code}")
        raise HTTPException(status_code=404, detail="Shared run not found")

    run_logger.debug(f"Загрузка информации о владельце | Loading owner info: user_id={run.user_id}")
    owner = user_crud.get_user_by_id(db, run.user_id)

    run_logger.info(f"Опубликованный забег успешно получен | Shared run retrieved: run_id={run.id}, owner_id={run.user_id}")
    return serialize_run(request, run, owner=owner)
