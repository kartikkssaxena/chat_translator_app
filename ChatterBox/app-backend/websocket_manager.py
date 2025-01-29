from fastapi import WebSocket
from typing import Dict, Set
from models import Profile

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[Profile, WebSocket] = {}

    async def connect(self, websocket: WebSocket, profile: Profile):
        self.active_connections[profile] = websocket
        await self.broadcast_profiles()

    async def disconnect(self, profile: Profile):
        if profile in self.active_connections:
            del self.active_connections[profile]
            await self.broadcast_profiles()

    async def broadcast_profiles(self):
        active_profiles = {
            str(profile.id): {
                "name": profile.name,
                "language": profile.language
            }
            for profile in self.active_connections.keys()
        }
        
        for connection in self.active_connections.values():
            await connection.send_json({
                "type": "profiles",
                "profiles": active_profiles
            })

    async def send_personal_message(self, message: str, profile: Profile):
        if profile in self.active_connections:
            await self.active_connections[profile].send_json(message)