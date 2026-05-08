from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index
from sqlalchemy.sql import func

from app.database import Base


class Conversation(Base):
    """
    Таблица диалогов между пользователями.
    Один диалог = один чат между двумя пользователями.
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)

    # первый участник
    user1_id = Column(Integer, ForeignKey("users.id"))

    # второй участник
    user2_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("conversation_users_idx", "user1_id", "user2_id", unique=True),
    )