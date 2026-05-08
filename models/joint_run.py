from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class JointRunChallenge(Base):
    __tablename__ = "joint_run_challenges"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opponent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    mode = Column(String(16), nullable=False)
    target_seconds = Column(Integer, nullable=True)
    target_distance_meters = Column(Float, nullable=True)
    status = Column(String(24), nullable=False, default="pending", server_default="pending")

    creator_ready = Column(Boolean, nullable=False, default=False, server_default="false")
    opponent_ready = Column(Boolean, nullable=False, default=False, server_default="false")

    creator_distance_meters = Column(Float, nullable=False, default=0, server_default="0")
    opponent_distance_meters = Column(Float, nullable=False, default=0, server_default="0")
    creator_duration_millis = Column(Integer, nullable=False, default=0, server_default="0")
    opponent_duration_millis = Column(Integer, nullable=False, default=0, server_default="0")
    creator_max_speed_kmh = Column(Float, nullable=True)
    opponent_max_speed_kmh = Column(Float, nullable=True)
    creator_latitude = Column(Float, nullable=True)
    creator_longitude = Column(Float, nullable=True)
    opponent_latitude = Column(Float, nullable=True)
    opponent_longitude = Column(Float, nullable=True)

    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    creator = relationship("User", foreign_keys=[creator_id])
    opponent = relationship("User", foreign_keys=[opponent_id])
    winner = relationship("User", foreign_keys=[winner_id])
    route_points = relationship("JointRunChallengeRoutePoint", back_populates="challenge", cascade="all, delete-orphan")

    __table_args__ = (
        Index("joint_run_conversation_status_idx", "conversation_id", "status"),
    )
