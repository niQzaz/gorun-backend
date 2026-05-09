from urllib.parse import parse_qs

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.chat_serialization import serialize_message
from app.crud import chat_crud
from app.database import SessionLocal
from app.security.jwt_handler import decode_token
from app.websocket.connection_manager import ConnectionManager


router = APIRouter()
manager = ConnectionManager()


@router.websocket("/chat/ws/{conversation_id}")
async def chat_ws(websocket: WebSocket, conversation_id: int):
    query_params = parse_qs(websocket.url.query)
    token_values = query_params.get("token")

    if not token_values:
        await websocket.close(code=1008)
        return

    token = token_values[0]

    try:
        payload = decode_token(token)
        user_id = payload["user_id"]
    except Exception:
        await websocket.close(code=1008)
        return

    db: Session = SessionLocal()

    try:
        if not chat_crud.is_user_in_conversation(db, user_id, conversation_id):
            await websocket.close(code=1008)
            return

        await manager.connect(conversation_id, websocket)

        while True:
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                raise
            except Exception:
                await websocket.send_json({
                    "type": "error",
                    "detail": "Invalid message payload"
                })
                continue

            content = data.get("content")
            client_message_id = data.get("client_message_id")

            if not isinstance(content, str):
                await websocket.send_json({
                    "type": "error",
                    "detail": "Field 'content' must be a string"
                })
                continue

            if client_message_id is not None and not isinstance(client_message_id, str):
                await websocket.send_json({
                    "type": "error",
                    "detail": "Field 'client_message_id' must be a string"
                })
                continue

            try:
                message = chat_crud.create_message(
                    db,
                    conversation_id,
                    user_id,
                    content,
                    client_message_id=client_message_id,
                    message_type="text"
                )
            except ValueError as exc:
                await websocket.send_json({
                    "type": "error",
                    "detail": str(exc)
                })
                continue

            await manager.broadcast(
                conversation_id,
                {
                    "type": "message",
                    **serialize_message(message)
                }
            )

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(conversation_id, websocket)
        db.close()
