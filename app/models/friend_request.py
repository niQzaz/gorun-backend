"""
Модель заявки в друзья.

Каждая запись — это одна заявка между двумя пользователями.
"""

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from datetime import datetime

from app.database import Base


class FriendRequest(Base):

    __tablename__ = "friend_requests"

    # уникальный id заявки
    id = Column(Integer, primary_key=True, index=True)

    # кто отправил заявку
    requester_id = Column(Integer, ForeignKey("users.id"))

    # кому отправили заявку
    receiver_id = Column(Integer, ForeignKey("users.id"))

    # статус заявки
    status = Column(String, default="pending")

    # дата создания
    created_at = Column(DateTime, default=datetime.utcnow)