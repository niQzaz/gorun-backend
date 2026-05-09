from datetime import datetime

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.conversations import Conversation
from app.models.message import Message


def _normalize_participants(user1: int, user2: int) -> tuple[int, int]:
    return (user1, user2) if user1 < user2 else (user2, user1)


def is_user_in_conversation(db: Session, user_id: int, conversation_id: int):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        or_(
            Conversation.user1_id == user_id,
            Conversation.user2_id == user_id
        )
    ).first()

    return conversation is not None


def get_or_create_conversation(db: Session, user1: int, user2: int):
    first_user_id, second_user_id = _normalize_participants(user1, user2)

    conversation = db.query(Conversation).filter(
        or_(
            and_(
                Conversation.user1_id == first_user_id,
                Conversation.user2_id == second_user_id
            ),
            and_(
                Conversation.user1_id == second_user_id,
                Conversation.user2_id == first_user_id
            )
        )
    ).first()

    if conversation:
        return conversation

    new_conversation = Conversation(
        user1_id=first_user_id,
        user2_id=second_user_id
    )

    db.add(new_conversation)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(new_conversation)

    return new_conversation


def create_message(db: Session,
                   conversation_id: int,
                   sender_id: int,
                   content: str | None,
                   client_message_id: str | None = None,
                   message_type: str = "text",
                   image_url: str | None = None,
                   shared_run: dict | None = None,
                   joint_run_challenge_id: int | None = None):
    normalized_type = (message_type or "text").strip().lower()
    normalized_content = content.strip() if content else ""
    normalized_client_message_id = client_message_id.strip() if client_message_id else None

    if normalized_client_message_id:
        existing_message = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.sender_id == sender_id,
                Message.client_message_id == normalized_client_message_id
            )
            .order_by(Message.id.desc())
            .first()
        )
        if existing_message is not None:
            return existing_message

    if normalized_type not in {"text", "image", "shared_run", "joint_run"}:
        raise ValueError("Unsupported message type")

    if normalized_type == "text" and not normalized_content:
        raise ValueError("Message content cannot be empty")

    if normalized_type == "image" and not image_url:
        raise ValueError("Image URL is required")

    if normalized_type == "shared_run":
        if not shared_run or not shared_run.get("share_code"):
            raise ValueError("Shared run data is required")
        if not normalized_content:
            normalized_content = f"Run: {shared_run.get('name', 'Shared run')}"

    if normalized_type == "joint_run":
        if not joint_run_challenge_id:
            raise ValueError("Joint run challenge is required")
        if not normalized_content:
            normalized_content = "Совместный забег"

    if normalized_type == "image" and not normalized_content:
        normalized_content = "Photo"

    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=normalized_content,
        client_message_id=normalized_client_message_id,
        message_type=normalized_type,
        image_url=image_url,
        joint_run_challenge_id=joint_run_challenge_id,
        is_read=False,
    )

    if shared_run:
        message.shared_run_code = shared_run.get("share_code")
        message.shared_run_name = shared_run.get("name")
        message.shared_run_distance_km = shared_run.get("distance_km")
        message.shared_run_duration_millis = shared_run.get("duration_millis")
        message.shared_run_performed_at = shared_run.get("performed_at")

    db.add(message)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(message)

    return message


def get_message_by_joint_run(db: Session, challenge_id: int) -> Message | None:
    return (
        db.query(Message)
        .filter(Message.joint_run_challenge_id == challenge_id)
        .order_by(Message.id.desc())
        .first()
    )


def mark_conversation_messages_as_read(db: Session, conversation_id: int, reader_id: int) -> list[int]:
    unread_messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != reader_id,
            Message.is_read.is_(False)
        )
        .order_by(Message.id.asc())
        .all()
    )

    if not unread_messages:
        return []

    updated_ids: list[int] = []
    for message in unread_messages:
        message.is_read = True
        updated_ids.append(message.id)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return updated_ids


def get_messages(
    db: Session,
    conversation_id: int,
    limit: int = 50,
    offset: int = 0
):
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_conversation_by_id(db: Session, conversation_id: int):
    return db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()


def get_last_message(db: Session, conversation_id: int):
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .first()
    )


def get_last_messages_map(db: Session, conversation_ids: list[int]) -> dict[int, Message]:
    if not conversation_ids:
        return {}

    latest_message_ids = (
        db.query(
            Message.conversation_id.label("conversation_id"),
            func.max(Message.id).label("message_id")
        )
        .filter(Message.conversation_id.in_(conversation_ids))
        .group_by(Message.conversation_id)
        .subquery()
    )

    messages = (
        db.query(Message)
        .join(latest_message_ids, Message.id == latest_message_ids.c.message_id)
        .all()
    )

    return {message.conversation_id: message for message in messages}


def get_user_conversations(db: Session, user_id: int):
    return (
        db.query(Conversation)
        .filter(
            or_(
                Conversation.user1_id == user_id,
                Conversation.user2_id == user_id
            )
        )
        .order_by(Conversation.created_at.desc(), Conversation.id.desc())
        .all()
    )


def get_conversation(db: Session, user1_id: int, user2_id: int):
    return db.query(Conversation).filter(
        ((Conversation.user1_id == user1_id) & (Conversation.user2_id == user2_id)) |
        ((Conversation.user1_id == user2_id) & (Conversation.user2_id == user1_id))
    ).first()
