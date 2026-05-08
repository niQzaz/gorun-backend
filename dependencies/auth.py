from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.jwt_handler import decode_token
from app.crud import user_crud


security = HTTPBearer()


def get_current_user(credentials=Depends(security), db: Session = Depends(get_db)):
    """
    Получаем пользователя из JWT токена
    """

    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id = payload["user_id"]

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = user_crud.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user