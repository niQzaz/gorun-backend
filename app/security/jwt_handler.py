# Работа с JWT токенами

import jwt
from datetime import datetime, timedelta

from app.config import settings

# Секретный ключ
SECRET_KEY = settings.SECRET_KEY

# Алгоритм шифрования
ALGORITHM = settings.ALGORITHM

# Время жизни токена
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(user_id: int):
    """
    Создание JWT токена
    """

    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def decode_token(token: str):
    """
    Декодирование токена
    """

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    return payload