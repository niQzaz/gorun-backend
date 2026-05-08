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
    target_user = user_crud.get_user_by_id(db, user_id)

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself")

    existing = friend_crud.friendship_exists(
        db,
        current_user.id,
        user_id
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Friend request already exists"
        )

    request = friend_crud.create_friend_request(
        db,
        current_user.id,
        user_id
    )

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

    requests = friend_crud.get_user_friend_requests(
        db,
        current_user.id
    )

    result = []

    for r in requests:

        sender = user_crud.get_user_by_id(db, r.requester_id)

        result.append({
            "request_id": r.id,
            "from_user": serialize_user(request, sender)
        })

    return result


@router.post("/reject/{request_id}")
def reject_request(request_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):

    req = friend_crud.get_request_by_id(db, request_id, current_user.id)

    if not req:
        raise HTTPException(404, "Request not found")

    friend_crud.update_request_status(db, req, "rejected")

    return {"status": "rejected"}



@router.post("/accept/{request_id}")
def accept_request(request_id: int,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):

    result = friend_crud.accept_friend_request(
        db,
        request_id,
        current_user.id
    )

    if not result:
        raise HTTPException(404, "Request not found")

    return {"status": "accepted"}


@router.get("/list", response_model=List[FriendResponse])
def get_friends(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    friends = friend_crud.get_friends(
        db,
        current_user.id
    )

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

    return result
