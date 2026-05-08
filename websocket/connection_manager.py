from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, conversation_id: int, websocket: WebSocket):
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []

        if websocket not in self.active_connections[conversation_id]:
            self.active_connections[conversation_id].append(websocket)

    def disconnect(self, conversation_id: int, websocket: WebSocket):
        connections = self.active_connections.get(conversation_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.active_connections[conversation_id]

    async def broadcast(self, conversation_id: int, message: dict):
        connections = list(self.active_connections.get(conversation_id, []))
        dead_connections: List[WebSocket] = []

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(conversation_id, connection)
