import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import user_crud
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.user_run import UserRun
from app.schemas.user_schema import (
    ApiMessageResponse,
    ChangePasswordRequest,
    LeaderboardEntryResponse,
    UpdateNicknameRequest,
    UserResponse,
)
from app.security.hashing import hash_password


AVATARS_DIR = Path(__file__).resolve().parent.parent / "media" / "avatars"
AVATARS_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/users", tags=["Users"])


def build_public_avatar_url(request: Request, avatar_path: str | None) -> str | None:
    if not avatar_path:
        return None

    return str(request.url_for("media", path=avatar_path))


def serialize_user(request: Request, user) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar_url": build_public_avatar_url(request, user.avatar_url)
    }


def delete_avatar_file(avatar_path: str | None) -> None:
    if not avatar_path:
        return

    file_path = (Path(__file__).resolve().parent.parent / "media" / avatar_path).resolve()
    media_root = (Path(__file__).resolve().parent.parent / "media").resolve()
    if media_root not in file_path.parents:
        return

    if file_path.exists() and file_path.is_file():
        file_path.unlink()


async def save_avatar_file(user_id: int, avatar: UploadFile) -> str:
    if not avatar.content_type or not avatar.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Avatar must be an image")

    suffix = Path(avatar.filename or "").suffix or ".jpg"
    filename = f"user_{user_id}_{uuid.uuid4().hex}{suffix.lower()}"
    relative_path = f"avatars/{filename}"
    file_path = AVATARS_DIR / filename

    with file_path.open("wb") as output_file:
        while True:
            chunk = await avatar.read(1024 * 1024)
            if not chunk:
                break
            output_file.write(chunk)

    await avatar.close()
    return relative_path


@router.get("/search", response_model=list[UserResponse])
def search_users(
    username: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    users = user_crud.search_users(db, username)

    return [
        serialize_user(request, user)
        for user in users
        if user.id != current_user.id
    ]


def build_leaderboard_entries(
    request: Request,
    db: Session,
    metric: str,
):
    total_distance_expr = func.coalesce(func.sum(UserRun.distance_km), 0.0).label("total_distance_km")
    total_runs_expr = func.count(UserRun.id).label("total_runs")
    total_duration_expr = func.coalesce(func.sum(UserRun.duration_millis), 0).label("total_duration_millis")

    rows = (
        db.query(
            User,
            total_distance_expr,
            total_runs_expr,
            total_duration_expr,
        )
        .outerjoin(UserRun, UserRun.user_id == User.id)
        .group_by(User.id)
        .all()
    )

    entries = []
    for user, total_distance_km, total_runs, total_duration_millis in rows:
        distance_value = float(total_distance_km or 0.0)
        duration_value = int(total_duration_millis or 0)
        average_pace = None
        if distance_value > 0.0 and duration_value > 0:
            average_pace = (duration_value / 60000.0) / distance_value

        entries.append({
            "user": user,
            "total_distance_km": distance_value,
            "total_runs": int(total_runs or 0),
            "average_pace_min_per_km": average_pace,
        })

    if metric == "pace":
        entries = [
            entry for entry in entries
            if entry["average_pace_min_per_km"] is not None
        ]
        entries.sort(key=lambda entry: (
            entry["average_pace_min_per_km"],
            -entry["total_distance_km"],
            -entry["total_runs"],
            (entry["user"].nickname or "").lower(),
            (entry["user"].username or "").lower(),
        ))
    else:
        entries.sort(key=lambda entry: (
            -entry["total_distance_km"],
            -entry["total_runs"],
            (entry["user"].nickname or "").lower(),
            (entry["user"].username or "").lower(),
        ))

    leaderboard = []
    for index, entry in enumerate(entries, start=1):
        leaderboard.append({
            "rank": index,
            "user": serialize_user(request, entry["user"]),
            "total_distance_km": entry["total_distance_km"],
            "total_runs": entry["total_runs"],
            "average_pace_min_per_km": entry["average_pace_min_per_km"],
        })

    return leaderboard


@router.get("/leaderboard", response_model=list[LeaderboardEntryResponse])
def get_leaderboard(
    request: Request,
    metric: str = Query("distance"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    normalized_metric = (metric or "distance").strip().lower()
    if normalized_metric not in {"distance", "pace"}:
        raise HTTPException(status_code=400, detail="Unsupported leaderboard metric")

    return build_leaderboard_entries(request, db, normalized_metric)


@router.get("/leaderboard/distance", response_model=list[LeaderboardEntryResponse])
def get_distance_leaderboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return build_leaderboard_entries(request, db, "distance")


@router.get("/leaderboard/pace", response_model=list[LeaderboardEntryResponse])
def get_pace_leaderboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return build_leaderboard_entries(request, db, "pace")


@router.get("/me/profile", response_model=UserResponse)
def get_my_profile(
    request: Request,
    current_user=Depends(get_current_user)
):
    return serialize_user(request, current_user)


@router.put("/me/profile", response_model=UserResponse)
@router.patch("/me/profile", response_model=UserResponse)
def update_my_profile(
    data: UpdateNicknameRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    nickname = data.nickname.strip()

    if not nickname:
        raise HTTPException(status_code=400, detail="Nickname cannot be empty")

    user = user_crud.update_nickname(db, current_user, nickname)
    return serialize_user(request, user)


@router.post("/me/change-password", response_model=ApiMessageResponse)
@router.put("/me/change-password", response_model=ApiMessageResponse)
@router.patch("/me/change-password", response_model=ApiMessageResponse)
def change_my_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_password = data.new_password.strip()

    if not new_password:
        raise HTTPException(status_code=400, detail="New password cannot be empty")

    user_crud.update_password_hash(db, current_user, hash_password(new_password))
    return {"message": "Password changed successfully"}


@router.post("/me/avatar", response_model=UserResponse)
@router.put("/me/avatar", response_model=UserResponse)
@router.patch("/me/avatar", response_model=UserResponse)
async def upload_my_avatar(
    request: Request,
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    old_avatar_path = current_user.avatar_url
    avatar_path = await save_avatar_file(current_user.id, avatar)
    user = user_crud.update_avatar_url(db, current_user, avatar_path)
    if old_avatar_path and old_avatar_path != avatar_path:
        delete_avatar_file(old_avatar_path)
    return serialize_user(request, user)
