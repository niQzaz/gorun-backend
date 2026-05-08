from sqlalchemy import Column, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class JointRunChallengeRoutePoint(Base):
    __tablename__ = "joint_run_challenge_route_points"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("joint_run_challenges.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    sequence_index = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elapsed_time_millis = Column(Integer, nullable=False)
    distance_meters = Column(Float, nullable=False)

    challenge = relationship("JointRunChallenge", back_populates="route_points")

    __table_args__ = (
        Index("joint_run_route_challenge_user_idx", "challenge_id", "user_id"),
        Index("joint_run_route_sequence_idx", "challenge_id", "user_id", "sequence_index"),
    )
