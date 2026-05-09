"""
Router системы друзей.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import friend_crud
from app.dependencies.auth import get_current_user
from app.crud import user_crud
from typing import List
from app.schemas.friend_schema import FriendResponse, FriendRequestWithUser
from app.routers.user_router import serialize_user
from app.logger import friend_logger


router = APIRouter(
    prefix="/friends",
    tags=["friends"]
)


@router.post("/request")
def send_friend_request(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Отправляет заявку в друзья.
    """
    friend_logger.info(f"Отправка заявки в друзья | Sending friend request: from_user_id={current_user.id} to_user_id={user_id}")

    target_user = user_crud.get_user_by_id(db, user_id)

    if not target_user:
        friend_logger.warning(f"Заявка отклонена: пользователь не найден | Request rejected: user not found - target_user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user_id:
        friend_logger.warning(f"Заявка отклонена: попытка добавить себя | Request rejected: cannot add yourself - user_id={current_user.id}")
        raise HTTPException(status_code=400, detail="Cannot add yourself")

    existing = friend_crud.friendship_exists(
        db,
        current_user.id,
        user_id
    )

    if existing:
        friend_logger.warning(f"Заявка отклонена: заявка уже существует | Request rejected: already exists - from={current_user.id}, to={user_id}")
        raise HTTPException(
            status_code=400,
            detail="Friend request already exists"
        )

    request = friend_crud.create_friend_request(
        db,
        current_user.id,
        user_id
    )

    friend_logger.info(f"Заявка в друзья успешно отправлена | Friend request sent successfully: request_id={request.id}, from={current_user.id}, to={user_id}")
    return {
        "message": "Friend request sent",
        "request_id": request.id
    }

@router.get("/requests", response_model=List[FriendRequestWithUser])
def get_requests(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    friend_logger.info(f"Получение списка заявок в друзья | Getting friend requests: user_id={current_user.id}")

    requests = friend_crud.get_user_friend_requests(
        db,
        current_user.id
    )

    friend_logger.debug(f"Найдено заявок | Found requests: count={len(requests)}, user_id={current_user.id}")

    result = []

    for r in requests:

        sender = user_crud.get_user_by_id(db, r.requester_id)

        result.append({
            "request_id": r.id,
            "from_user": serialize_user(request, sender)
        })

    friend_logger.info(f"Список заявок успешно получен | Requests list retrieved: count={len(result)}, user_id={current_user.id}")
    return result


@router.post("/reject/{request_id}")
def reject_request(request_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    friend_logger.info(f"Отклонение заявки в друзья | Rejecting friend request: request_id={request_id}, user_id={current_user.id}")

    req = friend_crud.get_request_by_id(db, request_id, current_user.id)

    if not req:
        friend_logger.warning(f"Заявка не найдена | Request not found: request_id={request_id}, user_id={current_user.id}")
        raise HTTPException(404, "Request not found")

    friend_crud.update_request_status(db, req, "rejected")

    friend_logger.info(f"Заявка отклонена | Request rejected: request_id={request_id}, from_user={req.requester_id}, by_user={current_user.id}")
    return {"status": "rejected"}



@router.post("/accept/{request_id}")
def accept_request(request_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    friend_logger.info(f"Принятие заявки в друзья | Accepting friend request: request_id={request_id}, user_id={current_user.id}")

    result = friend_crud.accept_friend_request(
        db,
        request_id,
        current_user.id
    )

    if not result:
        friend_logger.warning(f"Заявка не найдена | Request not found: request_id={request_id}, user_id={current_user.id}")
        raise HTTPException(404, "Request not found")

    friend_logger.info(f"Заявка принята, дружба установлена | Request accepted, friendship established: request_id={request_id}, user_id={current_user.id}")
    return {"status": "accepted"}


@router.get("/list", response_model=List[FriendResponse])
def get_friends(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    friend_logger.info(f"Получение списка друзей | Getting friends list: user_id={current_user.id}")

    friends = friend_crud.get_friends(
        db,
        current_user.id
    )

    friend_logger.debug(f"Найдено друзей | Found friends: count={len(friends)}, user_id={current_user.id}")

    result = []

    for f in friends:

        friend_id = (
            f.user2_id
            if f.user1_id == current_user.id
            else f.user1_id
        )

        result.append({
            "friend_id": friend_id,
            "friendship_id": f.id
        })

    friend_logger.info(f"Список друзей успешно получен | Friends list retrieved: count={len(result)}, user_id={current_user.id}")
    return result
