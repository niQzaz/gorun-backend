from fastapi import Request

from app.models.joint_run import JointRunChallenge
from app.models.message import Message


def build_public_media_url(request: Request | None, media_path: str | None) -> str | None:
    if not media_path:
        return None

    normalized_path = media_path.lstrip("/")
    if normalized_path.startswith("media/"):
        normalized_path = normalized_path[len("media/"):]

    if request is not None:
        return str(request.url_for("media", path=normalized_path))

    return "/media/" + normalized_path


def serialize_user_preview(request: Request | None, user) -> dict | None:
    if user is None:
        return None

    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar_url": build_public_media_url(request, user.avatar_url),
    }


def serialize_joint_run(challenge: JointRunChallenge | None, request: Request | None = None) -> dict | None:
    if challenge is None:
        return None

    return {
        "id": challenge.id,
        "conversation_id": challenge.conversation_id,
        "creator_id": challenge.creator_id,
        "opponent_id": challenge.opponent_id,
        "mode": challenge.mode,
        "target_seconds": challenge.target_seconds,
        "target_distance_meters": challenge.target_distance_meters,
        "status": challenge.status,
        "creator_ready": bool(challenge.creator_ready),
        "opponent_ready": bool(challenge.opponent_ready),
        "creator_distance_meters": challenge.creator_distance_meters or 0,
        "opponent_distance_meters": challenge.opponent_distance_meters or 0,
        "creator_duration_millis": challenge.creator_duration_millis or 0,
        "opponent_duration_millis": challenge.opponent_duration_millis or 0,
        "creator_max_speed_kmh": challenge.creator_max_speed_kmh,
        "opponent_max_speed_kmh": challenge.opponent_max_speed_kmh,
        "creator_latitude": challenge.creator_latitude,
        "creator_longitude": challenge.creator_longitude,
        "opponent_latitude": challenge.opponent_latitude,
        "opponent_longitude": challenge.opponent_longitude,
        "winner_id": challenge.winner_id,
        "started_at": challenge.started_at.isoformat() if challenge.started_at else None,
        "finished_at": challenge.finished_at.isoformat() if challenge.finished_at else None,
        "creator": serialize_user_preview(request, challenge.creator),
        "opponent": serialize_user_preview(request, challenge.opponent),
    }


def serialize_message(message: Message, request: Request | None = None) -> dict:
    shared_run = None
    if message.shared_run_code:
        shared_run = {
            "share_code": message.shared_run_code,
            "name": message.shared_run_name or "Shared run",
            "distance_km": message.shared_run_distance_km or 0,
            "duration_millis": message.shared_run_duration_millis or 0,
            "performed_at": (message.shared_run_performed_at or message.created_at).isoformat(),
        }

    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "sender_id": message.sender_id,
        "content": message.content or "",
        "client_message_id": message.client_message_id,
        "message_type": message.message_type or "text",
        "image_url": build_public_media_url(request, message.image_url),
        "shared_run": shared_run,
        "joint_run": serialize_joint_run(message.joint_run_challenge, request),
        "is_read": bool(message.is_read),
        "created_at": message.created_at.isoformat(),
    }
