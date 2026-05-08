"""
Схемы для работы с заявками в друзья.
"""

from pydantic import BaseModel
from app.schemas.user_schema import UserResponse, UserOut


class FriendRequestCreate(BaseModel):

    receiver_id: int

class FriendResponse(BaseModel):
    friend_id: int
    friendship_id: int


class FriendRequestWithUser(BaseModel):
    request_id: int
    from_user: UserResponse

class FriendRequestResponse(BaseModel):

    id: int
    requester_id: int
    receiver_id: int
    status: str

    class Config:
        from_attributes = True


class FriendOut(BaseModel):
    user: UserOut

    class Config:
        from_attributes = True