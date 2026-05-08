from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)

    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))

    content = Column(Text)
    client_message_id = Column(String(64), nullable=True)
    message_type = Column(String(32), nullable=False, default="text", server_default="text")
    image_url = Column(Text, nullable=True)
    shared_run_code = Column(String(64), nullable=True)
    shared_run_name = Column(String(120), nullable=True)
    shared_run_distance_km = Column(Float, nullable=True)
    shared_run_duration_millis = Column(Integer, nullable=True)
    shared_run_performed_at = Column(DateTime(timezone=True), nullable=True)
    joint_run_challenge_id = Column(Integer, ForeignKey("joint_run_challenges.id", ondelete="SET NULL"), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, server_default="false")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    joint_run_challenge = relationship("JointRunChallenge")

    __table_args__ = (
        Index("messages_conversation_idx", "conversation_id"),
        Index("messages_created_idx", "created_at"),
        Index("messages_client_message_idx", "conversation_id", "sender_id", "client_message_id"),
    )
