from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(
        User.username == username
    ).first()


def create_user(db: Session, username: str, nickname: str, password_hash: str):
    new_user = User(
        username=username,
        nickname=nickname,
        password_hash=password_hash
    )

    db.add(new_user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(new_user)

    return new_user


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def search_users(db: Session, username: str):
    return (
        db.query(User)
        .filter(User.username.ilike(f"%{username}%"))
        .order_by(User.username.asc())
        .limit(20)
        .all()
    )


def _commit_user(db: Session, user: User):
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(user)
    return user


def update_nickname(db: Session, user: User, nickname: str):
    user.nickname = nickname.strip()
    return _commit_user(db, user)


def update_password_hash(db: Session, user: User, password_hash: str):
    user.password_hash = password_hash
    return _commit_user(db, user)


def update_avatar_url(db: Session, user: User, avatar_url: str | None):
    user.avatar_url = avatar_url
    return _commit_user(db, user)
