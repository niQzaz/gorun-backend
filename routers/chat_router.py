import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.chat_serialization import serialize_message
from app.crud import chat_crud, friend_crud, user_crud
from app.crud import joint_run_crud
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.joint_run import JointRunChallenge
from app.models.user_run import UserRun
from app.routers.chat_ws import manager
from app.routers.user_router import serialize_user
from app.schemas.chat_schema import (
    ChatPreview,
    ConversationResponse,
    JointRunCreate,
    JointRunLiveUpdate,
    JointRunRouteResponse,
    MessageCreate,
    MessageResponse,
    ReadReceiptResponse,
)


CHAT_IMAGES_DIR = Path(__file__).resolve().parent.parent / "media" / "chat_images"
CHAT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


async def save_chat_image_file(image: UploadFile) -> str:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Attachment must be an image")

    suffix = Path(image.filename or "").suffix or ".jpg"
    filename = f"chat_{uuid.uuid4().hex}{suffix.lower()}"
    relative_path = f"chat_images/{filename}"
    file_path = CHAT_IMAGES_DIR / filename

    with file_path.open("wb") as output_file:
        while True:
            chunk = await image.read(1024 * 1024)
            if not chunk:
                break
            output_file.write(chunk)

    await image.close()
    return relative_path


def delete_chat_image_file(image_path: str | None) -> None:
    if not image_path:
        return

    file_path = (Path(__file__).resolve().parent.parent / "media" / image_path).resolve()
    media_root = (Path(__file__).resolve().parent.parent / "media").resolve()
    if media_root not in file_path.parents:
        return

    if file_path.exists() and file_path.is_file():
        file_path.unlink()


def ensure_conversation_access(db: Session, current_user_id: int, conversation_id: int) -> None:
    if not chat_crud.is_user_in_conversation(db, current_user_id, conversation_id):
        raise HTTPException(status_code=403, detail="Access denied")


def build_shared_run_payload(db: Session, current_user, share_code: str) -> dict:
    run = db.query(UserRun).filter(UserRun.share_code == share_code).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.user_id != current_user.id and not run.is_shared:
        raise HTTPException(status_code=403, detail="Run is not available for sharing")

    if run.user_id == current_user.id and not run.is_shared:
        run.is_shared = True
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(run)

    return {
        "share_code": run.share_code,
        "name": run.name,
        "distance_km": run.distance_km,
        "duration_millis": run.duration_millis,
        "performed_at": run.performed_at,
    }


def get_conversation_opponent_id(db: Session, conversation_id: int, current_user_id: int) -> int:
    conversation = chat_crud.get_conversation_by_id(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user1_id == current_user_id:
        return conversation.user2_id
    if conversation.user2_id == current_user_id:
        return conversation.user1_id

    raise HTTPException(status_code=403, detail="Access denied")


def get_joint_run_for_user(db: Session, challenge_id: int, user_id: int) -> JointRunChallenge:
    challenge = db.query(JointRunChallenge).filter(JointRunChallenge.id == challenge_id).first()
    if challenge is None:
        raise HTTPException(status_code=404, detail="Joint run not found")

    if user_id not in {challenge.creator_id, challenge.opponent_id}:
        raise HTTPException(status_code=403, detail="Access denied")

    return challenge


def validate_joint_run_payload(data: JointRunCreate) -> tuple[str, int | None, float | None]:
    mode = (data.mode or "").strip().lower()
    if mode not in {"time", "distance"}:
        raise HTTPException(status_code=400, detail="Unsupported joint run mode")

    if mode == "time":
        if data.target_seconds is None or data.target_seconds <= 0:
            raise HTTPException(status_code=400, detail="Target time is required")
        return mode, data.target_seconds, None

    if data.target_distance_meters is None or data.target_distance_meters <= 0:
        raise HTTPException(status_code=400, detail="Target distance is required")

    return mode, None, data.target_distance_meters


def serialize_joint_run_message(db: Session, request: Request, challenge_id: int) -> dict:
    message = chat_crud.get_message_by_joint_run(db, challenge_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Joint run message not found")

    return serialize_message(message, request)


async def broadcast_joint_run_message(db: Session, request: Request, challenge_id: int) -> dict:
    message = chat_crud.get_message_by_joint_run(db, challenge_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Joint run message not found")

    serialized_message = serialize_joint_run_message(db, request, challenge_id)
    await manager.broadcast(message.conversation_id, {"type": "message", **serialized_message})
    return serialized_message


def reset_joint_run_readiness(challenge: JointRunChallenge) -> None:
    challenge.creator_ready = False
    challenge.opponent_ready = False


def mark_joint_run_finished_if_needed(challenge: JointRunChallenge) -> None:
    if challenge.status not in {"running", "ready"}:
        return

    should_finish = False
    if challenge.mode == "time" and challenge.target_seconds:
        target_millis = challenge.target_seconds * 1000
        should_finish = (
            challenge.creator_duration_millis >= target_millis
            or challenge.opponent_duration_millis >= target_millis
        )
    elif challenge.mode == "distance" and challenge.target_distance_meters:
        should_finish = (
            challenge.creator_distance_meters >= challenge.target_distance_meters
            or challenge.opponent_distance_meters >= challenge.target_distance_meters
        )

    if not should_finish:
        return

    challenge.status = "finished"
    challenge.finished_at = func.now()

    # Определяем победителя по дистанции
    if challenge.creator_distance_meters > challenge.opponent_distance_meters:
        challenge.winner_id = challenge.creator_id
    elif challenge.opponent_distance_meters > challenge.creator_distance_meters:
        challenge.winner_id = challenge.opponent_id
    else:
        # При равных дистанциях сравниваем по времени (меньше время = победитель)
        if challenge.creator_duration_millis < challenge.opponent_duration_millis:
            challenge.winner_id = challenge.creator_id
        elif challenge.opponent_duration_millis < challenge.creator_duration_millis:
            challenge.winner_id = challenge.opponent_id
        # Если и время равно - ничья (winner_id остается None)


@router.post("/start", response_model=ConversationResponse)
def start_chat(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself")

    target_user = user_crud.get_user_by_id(db, user_id)

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not friend_crud.friendship_exists(db, current_user.id, user_id):
        raise HTTPException(
            status_code=403,
            detail="You can start chats only with friends"
        )

    conversation = chat_crud.get_or_create_conversation(
        db,
        current_user.id,
        user_id
    )

    return conversation


@router.post("/send", response_model=MessageResponse)
async def send_message(
    data: MessageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ensure_conversation_access(db, current_user.id, data.conversation_id)

    try:
        if data.message_type == "shared_run":
            shared_run = build_shared_run_payload(db, current_user, (data.shared_run_code or "").strip())
            message = chat_crud.create_message(
                db,
                data.conversation_id,
                current_user.id,
                f"Run: {shared_run['name']}",
                client_message_id=data.client_message_id,
                message_type="shared_run",
                shared_run=shared_run,
            )
        else:
            message = chat_crud.create_message(
                db,
                data.conversation_id,
                current_user.id,
                data.content,
                client_message_id=data.client_message_id,
                message_type=data.message_type,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    serialized_message = serialize_message(message, request)
    await manager.broadcast(data.conversation_id, {"type": "message", **serialized_message})
    return serialized_message


@router.post("/{conversation_id}/joint-runs", response_model=MessageResponse)
async def create_joint_run(
    conversation_id: int,
    data: JointRunCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ensure_conversation_access(db, current_user.id, conversation_id)
    opponent_id = get_conversation_opponent_id(db, conversation_id, current_user.id)
    mode, target_seconds, target_distance_meters = validate_joint_run_payload(data)

    challenge = JointRunChallenge(
        conversation_id=conversation_id,
        creator_id=current_user.id,
        opponent_id=opponent_id,
        mode=mode,
        target_seconds=target_seconds,
        target_distance_meters=target_distance_meters,
        status="pending",
    )
    db.add(challenge)
    db.flush()

    title = "Совместный забег на время" if mode == "time" else "Совместный забег на расстояние"
    message = chat_crud.create_message(
        db,
        conversation_id,
        current_user.id,
        title,
        client_message_id=data.client_message_id,
        message_type="joint_run",
        joint_run_challenge_id=challenge.id,
    )

    serialized_message = serialize_message(message, request)
    await manager.broadcast(conversation_id, {"type": "message", **serialized_message})
    return serialized_message


@router.get("/joint-runs/{challenge_id}", response_model=MessageResponse)
async def get_joint_run(
    challenge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)
    return serialize_joint_run_message(db, request, challenge.id)


@router.post("/joint-runs/{challenge_id}/accept", response_model=MessageResponse)
async def accept_joint_run(
    challenge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)
    if current_user.id != challenge.opponent_id:
        raise HTTPException(status_code=403, detail="Only the opponent can accept this request")
    if challenge.status not in {"pending", "postponed"}:
        raise HTTPException(status_code=400, detail="Joint run cannot be accepted now")

    challenge.status = "accepted"
    reset_joint_run_readiness(challenge)
    db.commit()
    db.refresh(challenge)
    return await broadcast_joint_run_message(db, request, challenge.id)


@router.post("/joint-runs/{challenge_id}/postpone", response_model=MessageResponse)
async def postpone_joint_run(
    challenge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)
    if current_user.id != challenge.opponent_id:
        raise HTTPException(status_code=403, detail="Only the opponent can postpone this request")
    if challenge.status not in {"pending", "accepted"}:
        raise HTTPException(status_code=400, detail="Joint run cannot be postponed now")

    challenge.status = "postponed"
    reset_joint_run_readiness(challenge)
    db.commit()
    db.refresh(challenge)
    return await broadcast_joint_run_message(db, request, challenge.id)


@router.post("/joint-runs/{challenge_id}/restart", response_model=MessageResponse)
async def restart_joint_run(
    challenge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)
    if challenge.status not in {"postponed", "cancelled"}:
        raise HTTPException(status_code=400, detail="Joint run cannot be restarted now")

    challenge.status = "pending"
    reset_joint_run_readiness(challenge)
    db.commit()
    db.refresh(challenge)
    return await broadcast_joint_run_message(db, request, challenge.id)


@router.post("/joint-runs/{challenge_id}/cancel", response_model=MessageResponse)
async def cancel_joint_run(
    challenge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)
    if challenge.status in {"finished", "running"}:
        raise HTTPException(status_code=400, detail="Joint run cannot be cancelled now")

    challenge.status = "cancelled"
    reset_joint_run_readiness(challenge)
    db.commit()
    db.refresh(challenge)
    return await broadcast_joint_run_message(db, request, challenge.id)


@router.post("/joint-runs/{challenge_id}/ready", response_model=MessageResponse)
async def ready_joint_run(
    challenge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)
    if challenge.status not in {"accepted", "ready"}:
        raise HTTPException(status_code=400, detail="Joint run is not accepted")

    if current_user.id == challenge.creator_id:
        challenge.creator_ready = True
    else:
        challenge.opponent_ready = True

    if challenge.creator_ready and challenge.opponent_ready:
        challenge.status = "ready"
        challenge.started_at = func.now()

    db.commit()
    db.refresh(challenge)
    return await broadcast_joint_run_message(db, request, challenge.id)


@router.post("/joint-runs/{challenge_id}/live", response_model=MessageResponse)
async def update_joint_run_live(
    challenge_id: int,
    data: JointRunLiveUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)
    if challenge.status == "ready":
        challenge.status = "running"
    if challenge.status not in {"running", "finished"}:
        raise HTTPException(status_code=400, detail="Joint run is not running")

    if current_user.id == challenge.creator_id:
        challenge.creator_distance_meters = data.distance_meters
        challenge.creator_duration_millis = data.duration_millis
        challenge.creator_latitude = data.latitude
        challenge.creator_longitude = data.longitude
        if data.max_speed_kmh is not None:
            challenge.creator_max_speed_kmh = data.max_speed_kmh
    else:
        challenge.opponent_distance_meters = data.distance_meters
        challenge.opponent_duration_millis = data.duration_millis
        challenge.opponent_latitude = data.latitude
        challenge.opponent_longitude = data.longitude
        if data.max_speed_kmh is not None:
            challenge.opponent_max_speed_kmh = data.max_speed_kmh

    # Сохраняем точку маршрута, если есть координаты
    if data.latitude is not None and data.longitude is not None:
        joint_run_crud.save_route_point(
            db,
            challenge_id=challenge.id,
            user_id=current_user.id,
            latitude=data.latitude,
            longitude=data.longitude,
            elapsed_time_millis=data.duration_millis,
            distance_meters=data.distance_meters,
        )

    mark_joint_run_finished_if_needed(challenge)
    db.commit()
    db.refresh(challenge)
    return await broadcast_joint_run_message(db, request, challenge.id)


@router.get("/joint-runs/{challenge_id}/route", response_model=JointRunRouteResponse)
async def get_joint_run_route(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    challenge = get_joint_run_for_user(db, challenge_id, current_user.id)

    # Получаем точки маршрута для обоих участников
    all_route_points = joint_run_crud.get_route_points(db, challenge_id)

    creator_route = []
    opponent_route = []

    for point in all_route_points:
        route_point = {
            "sequence_index": point.sequence_index,
            "latitude": point.latitude,
            "longitude": point.longitude,
            "elapsed_time_millis": point.elapsed_time_millis,
            "distance_meters": point.distance_meters,
        }

        if point.user_id == challenge.creator_id:
            creator_route.append(route_point)
        elif point.user_id == challenge.opponent_id:
            opponent_route.append(route_point)

    return {
        "challenge_id": challenge.id,
        "creator_id": challenge.creator_id,
        "opponent_id": challenge.opponent_id,
        "creator_route": creator_route,
        "opponent_route": opponent_route,
    }


@router.post("/send-image", response_model=MessageResponse)
async def send_image(
    request: Request,
    conversation_id: int = Form(...),
    client_message_id: str | None = Form(default=None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ensure_conversation_access(db, current_user.id, conversation_id)

    saved_image_path = await save_chat_image_file(image)
    try:
        message = chat_crud.create_message(
            db,
            conversation_id,
            current_user.id,
            "Photo",
            client_message_id=client_message_id,
            message_type="image",
            image_url=saved_image_path,
        )
    except Exception:
        delete_chat_image_file(saved_image_path)
        raise

    serialized_message = serialize_message(message, request)
    await manager.broadcast(conversation_id, {"type": "message", **serialized_message})
    return serialized_message


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: int,
    request: Request,
    limit: int = 500,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    ensure_conversation_access(db, current_user.id, conversation_id)

    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be positive or zero")

    updated_message_ids = chat_crud.mark_conversation_messages_as_read(db, conversation_id, current_user.id)

    messages = chat_crud.get_messages(
        db,
        conversation_id,
        limit=limit,
        offset=offset
    )

    if updated_message_ids:
        await manager.broadcast(
            conversation_id,
            {
                "type": "read",
                "conversation_id": conversation_id,
                "reader_id": current_user.id,
                "message_ids": updated_message_ids,
            }
        )

    return [serialize_message(message, request) for message in messages]


@router.post("/{conversation_id}/read", response_model=ReadReceiptResponse)
async def mark_messages_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ensure_conversation_access(db, current_user.id, conversation_id)

    updated_message_ids = chat_crud.mark_conversation_messages_as_read(db, conversation_id, current_user.id)
    if updated_message_ids:
        await manager.broadcast(
            conversation_id,
            {
                "type": "read",
                "conversation_id": conversation_id,
                "reader_id": current_user.id,
                "message_ids": updated_message_ids,
            }
        )

    return {
        "conversation_id": conversation_id,
        "message_ids": updated_message_ids,
    }


@router.get("", response_model=list[ChatPreview])
def get_chats(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    conversations = chat_crud.get_user_conversations(db, current_user.id)
    conversation_ids = [conversation.id for conversation in conversations]
    last_messages = chat_crud.get_last_messages_map(db, conversation_ids)

    conversations.sort(
        key=lambda conversation: (
            last_messages.get(conversation.id).created_at
            if last_messages.get(conversation.id)
            else conversation.created_at
        ),
        reverse=True
    )

    result = []

    for conversation in conversations:
        other_id = (
            conversation.user2_id
            if conversation.user1_id == current_user.id
            else conversation.user1_id
        )
        other_user = user_crud.get_user_by_id(db, other_id)
        last_message = last_messages.get(conversation.id)

        if not other_user:
            continue

        result.append({
            "conversation_id": conversation.id,
            "user": serialize_user(request, other_user),
            "last_message": last_message.content if last_message else None,
            "last_message_time": last_message.created_at if last_message else None
        })

    return result
