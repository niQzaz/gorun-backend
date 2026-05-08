from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index
from sqlalchemy.sql import func

from app.database import Base


class Friend(Base):

    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)

    user1_id = Column(Integer, ForeignKey("users.id"))
    user2_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("friend_unique_relation", "user1_id", "user2_id", unique=True),
    )