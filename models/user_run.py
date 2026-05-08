import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRun(Base):
    __tablename__ = "user_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    performed_at = Column(DateTime(timezone=True), nullable=False)
    duration_millis = Column(Integer, nullable=False, default=0)
    distance_km = Column(Float, nullable=False, default=0)
    avg_speed_kmh = Column(Float, nullable=False, default=0)
    max_speed_kmh = Column(Float, nullable=False, default=0)
    pace_min_per_km = Column(Float, nullable=False, default=0)
    is_shared = Column(Boolean, nullable=False, default=False)
    share_code = Column(String, nullable=False, unique=True, default=lambda: uuid.uuid4().hex)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    route_points = relationship(
        "UserRunRoutePoint",
        cascade="all, delete-orphan",
        order_by="UserRunRoutePoint.sequence_index",
        back_populates="run",
    )


class UserRunRoutePoint(Base):
    __tablename__ = "user_run_route_points"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("user_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_index = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elapsed_time_millis = Column(Integer, nullable=False, default=0)
    distance_meters = Column(Float, nullable=False, default=0)

    run = relationship("UserRun", back_populates="route_points")
