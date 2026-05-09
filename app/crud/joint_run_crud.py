from sqlalchemy.orm import Session

from app.models.joint_run_route_point import JointRunChallengeRoutePoint


def save_route_point(
    db: Session,
    challenge_id: int,
    user_id: int,
    latitude: float,
    longitude: float,
    elapsed_time_millis: int,
    distance_meters: float,
) -> JointRunChallengeRoutePoint:
    # Получаем текущий максимальный sequence_index для этого пользователя в этом челлендже
    max_sequence = (
        db.query(JointRunChallengeRoutePoint.sequence_index)
        .filter(
            JointRunChallengeRoutePoint.challenge_id == challenge_id,
            JointRunChallengeRoutePoint.user_id == user_id,
        )
        .order_by(JointRunChallengeRoutePoint.sequence_index.desc())
        .first()
    )

    next_sequence = (max_sequence[0] + 1) if max_sequence else 0

    route_point = JointRunChallengeRoutePoint(
        challenge_id=challenge_id,
        user_id=user_id,
        sequence_index=next_sequence,
        latitude=latitude,
        longitude=longitude,
        elapsed_time_millis=elapsed_time_millis,
        distance_meters=distance_meters,
    )

    db.add(route_point)
    return route_point


def get_route_points(
    db: Session,
    challenge_id: int,
    user_id: int | None = None,
) -> list[JointRunChallengeRoutePoint]:
    query = db.query(JointRunChallengeRoutePoint).filter(
        JointRunChallengeRoutePoint.challenge_id == challenge_id
    )

    if user_id is not None:
        query = query.filter(JointRunChallengeRoutePoint.user_id == user_id)

    return query.order_by(
        JointRunChallengeRoutePoint.user_id,
        JointRunChallengeRoutePoint.sequence_index,
    ).all()
