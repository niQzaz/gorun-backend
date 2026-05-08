"""
CRUD операции для системы друзей.
"""

from sqlalchemy.orm import Session
from app.models.friend_request import FriendRequest
from sqlalchemy import and_, or_

from app.models.friend import Friend


def create_friend_request(db: Session, requester_id: int, receiver_id: int):

    request = FriendRequest(
        requester_id=requester_id,
        receiver_id=receiver_id
    )

    if friend_request_exists(db, requester_id, receiver_id):
        raise Exception("Request already exists")

    if friendship_exists(db, requester_id, receiver_id):
        raise Exception("Already friends")

    db.add(request)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    db.refresh(request)


    return request


def get_friends(db: Session, user_id: int):

    return db.query(Friend).filter(
        or_(
            Friend.user1_id == user_id,
            Friend.user2_id == user_id
        )
    ).all()


def accept_friend_request(db: Session, request_id: int, user_id: int):

    request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.receiver_id == user_id
    ).first()

    if not request:
        return None

    if request.status != "pending":
        return None

    # проверка дружбы
    if friendship_exists(db, request.requester_id, request.receiver_id):
        return request

    request.status = "accepted"

    friendship = Friend(
        user1_id=request.requester_id,
        user2_id=request.receiver_id
    )

    db.add(friendship)
    try:
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(request)

    return request


def get_user_friend_requests(db: Session, user_id: int):

    return db.query(FriendRequest).filter(
        FriendRequest.receiver_id == user_id,
        FriendRequest.status == "pending"
    ).all()






def get_request_by_id(db: Session, request_id: int, user_id: int):
    return (
        db.query(FriendRequest)
        .filter(
            FriendRequest.id == request_id,
            FriendRequest.receiver_id == user_id
        )
        .first()
    )








def update_request_status(db: Session, request: FriendRequest, status: str):

    request.status = status

    try:
        db.commit()
    except:
        db.rollback()
        raise
    db.refresh(request)

    return request

def friendship_exists(db: Session, user1: int, user2: int):
    """
    Проверяет, существует ли уже отношение между пользователями.

    Это защищает от:
    A -> B
    B -> A
    """

    if user1 == user2:
        return True

    return db.query(Friend).filter(
        or_(
            and_(
                Friend.user1_id == user1,
                Friend.user2_id == user2
            ),
            and_(
                Friend.user1_id == user2,
                Friend.user2_id == user1
            )
        )
    ).first()


def friend_request_exists(db: Session, user1: int, user2: int):

    return db.query(FriendRequest).filter(
        or_(
            and_(
                FriendRequest.requester_id == user1,
                FriendRequest.receiver_id == user2
            ),
            and_(
                FriendRequest.requester_id == user2,
                FriendRequest.receiver_id == user1
            )
        )
    ).first()