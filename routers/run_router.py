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
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Run name cannot be empty")

    performed_at = datetime.fromtimestamp(data.performed_at_millis / 1000.0, tz=timezone.utc)

    existing_run = get_existing_run_by_timestamp(db, current_user.id, performed_at)
    if existing_run is not None:
        return serialize_run(request, existing_run)

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
    except Exception:
        db.rollback()
        raise

    created_run = get_owned_run(db, run.id, current_user.id)
    if created_run is None:
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
    runs = (
        db.query(UserRun)
        .options(selectinload(UserRun.route_points))
        .filter(UserRun.user_id == current_user.id)
        .order_by(UserRun.performed_at.desc(), UserRun.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [serialize_run(request, run) for run in runs]


@router.post("/{run_id}/share", response_model=UserRunShareResponse)
def share_my_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    run = get_owned_run(db, run_id, current_user.id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if not run.is_shared:
        run.is_shared = True
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(run)

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
    run = (
        db.query(UserRun)
        .options(selectinload(UserRun.route_points))
        .filter(UserRun.share_code == share_code)
        .first()
    )

    if run is None or not run.is_shared:
        raise HTTPException(status_code=404, detail="Shared run not found")

    owner = user_crud.get_user_by_id(db, run.user_id)
    return serialize_run(request, run, owner=owner)
