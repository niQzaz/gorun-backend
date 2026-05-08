"""
Router авторизации.

Здесь находятся endpoints:

POST /auth/register
POST /auth/login
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schema import UserRegister, UserLogin
from app.crud import user_crud
from app.security.hashing import hash_password, verify_password
from app.security.jwt_handler import create_access_token
from app.schemas.user_schema import UserResponse, TokenResponse


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_username(db, user.username)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed = hash_password(user.password)

    new_user = user_crud.create_user(
        db,
        user.username,
        user.nickname,
        hashed
    )

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Логин пользователя
    """

    # Получаем пользователя из базы
    db_user = user_crud.get_user_by_username(db, user.username)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем пароль
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Создаем JWT
    token = create_access_token(db_user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
