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
from app.logger import auth_logger


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    auth_logger.info(f"Попытка регистрации нового пользователя | Registration attempt: username={user.username}")

    existing_user = user_crud.get_user_by_username(db, user.username)

    if existing_user:
        auth_logger.warning(f"Регистрация отклонена: имя пользователя уже существует | Registration rejected: username already exists - {user.username}")
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    auth_logger.debug(f"Хеширование пароля для пользователя | Hashing password for user: {user.username}")
    hashed = hash_password(user.password)

    auth_logger.info(f"Создание нового пользователя в БД | Creating new user in database: {user.username}")
    new_user = user_crud.create_user(
        db,
        user.username,
        user.nickname,
        hashed
    )

    auth_logger.info(f"Пользователь успешно зарегистрирован | User successfully registered: id={new_user.id}, username={new_user.username}")
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Логин пользователя
    """
    auth_logger.info(f"Попытка входа | Login attempt: username={user.username}")

    # Получаем пользователя из базы
    db_user = user_crud.get_user_by_username(db, user.username)

    if not db_user:
        auth_logger.warning(f"Вход отклонен: пользователь не найден | Login rejected: user not found - {user.username}")
        raise HTTPException(status_code=404, detail="User not found")

    auth_logger.debug(f"Проверка пароля для пользователя | Verifying password for user: {user.username}")
    # Проверяем пароль
    if not verify_password(user.password, db_user.password_hash):
        auth_logger.warning(f"Вход отклонен: неверный пароль | Login rejected: invalid password - username={user.username}, user_id={db_user.id}")
        raise HTTPException(status_code=401, detail="Invalid password")

    # Создаем JWT
    auth_logger.debug(f"Создание JWT токена | Creating JWT token for user_id={db_user.id}")
    token = create_access_token(db_user.id)

    auth_logger.info(f"Успешный вход | Successful login: user_id={db_user.id}, username={user.username}")
    return {
        "access_token": token,
        "token_type": "bearer"
    }
