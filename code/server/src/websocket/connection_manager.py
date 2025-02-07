import asyncio
from fastapi import WebSocket
from src.database.database_manager import DatabaseManager
import json


class ConnectionManager:
    def __init__(self, db_manager: DatabaseManager):
        self.active_connections = {}
        self.user_details = {}
        self.db_manager = db_manager

    async def broadcast_active_users(self):
        """Broadcast list of active users to all connected clients"""
        active_users = [
            {
                "device_id": id,
                "language": details["language"],
            }
            for id, details in self.user_details.items()
        ]
        broadcast_message = {
            "type": "active_users",
            "users": active_users,
        }
        for conn in self.active_connections.values():
            await conn.send_json(broadcast_message)

    async def connect(self, websocket: WebSocket):
        """Connect a new client and retrieve chat history"""
        await websocket.accept()
        data = await websocket.receive_json()
        device_id = data["sender"]
        client_ip = websocket.client.host
        self.active_connections[device_id] = websocket

        # Retrieve device language
        language = self.db_manager.get_device_language(device_id)

        # Store user details
        self.user_details[device_id] = {
            "websocket": websocket,
            "language": language,
            "ip_address": client_ip,
        }
        print(device_id, self.user_details[device_id])
        print(f"active connections: {self.active_connections}")
        await self.broadcast_active_users()

        # Retrieve and send chat history
        chat_history = self.db_manager.get_chat_history(device_id, device_id)
        for msg in chat_history:
            await websocket.send_json(
                {"sender": msg[0], "message": msg[1], "language": msg[3]}
            )
        print(f"Connected to server - device id: {device_id}")
        return language

    def disconnect(self, device_id: str):
        """Disconnect a client"""
        if device_id in self.active_connections:
            del self.active_connections[device_id]
        if device_id in self.user_details:
            del self.user_details[device_id]

    async def send_message(self, outgoing_data: dict, target_device: str):
        """Send message to a specific device"""
        print(f"All active connections: {self.active_connections}")
        if target_device in self.active_connections:
            print(f"Sending message to {target_device}")
            target_socket = self.active_connections[target_device]
            print(f"target_socket: {target_socket}")
            await target_socket.send_json(outgoing_data)
            print(f"Message sent to {target_device}")
