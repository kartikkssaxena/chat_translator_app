import asyncio
import websockets
from fastapi import WebSocket
from src.database.database_manager import DatabaseManager
from src.chat_history.chat_backup_handler import fetch_chat_history
import json


class ConnectionManager:
    def __init__(self, db_manager: DatabaseManager):
        self.active_connections = {}
        self.db_manager = db_manager
        self.server_socket = None

    async def connect(self, websocket: WebSocket, device_id: str):
        """Connect a new client and retrieve chat history"""
        await websocket.accept()
        self.active_connections[device_id] = websocket

        # Retrieve device language
        language = self.db_manager.get_device_language(device_id)
        return language

    def disconnect(self, device_id: str):
        """Disconnect a client"""
        if device_id in self.active_connections:
            del self.active_connections[device_id]

    async def send_message(
        self, sender: str, target_device: str, message: str, language: str
    ):
        """Send message to a specific device"""
        if target_device in self.active_connections:
            target_socket = self.active_connections[target_device]
            await target_socket.send_json(
                {"sender": sender, "message": message, "language": language}
            )

    async def connect_to_server(self, server_url: str):
        """Connect to the server and start listening for messages"""
        self.server_socket = await websockets.connect(server_url)
        asyncio.create_task(self.listen_to_server())

    async def broadcast_chat_history(self, chat_history: dict):
        """Broadcast chat history to all connected clients"""
        print("broadcast_chat_history called")
        print("chat_history:", json.dumps(chat_history, indent=4))

        for device_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(
                    {"type": "chat_history", "chat_history": chat_history}
                )
                print(f"Sent chat history to {device_id}")
            except Exception as e:
                print(f"Failed to send chat history to {device_id}: {e}")

    async def broadcast_active_users(self, active_users: dict):
        """Broadcast list of active users to all connected clients"""
        print("active users", active_users)
        for device_id, websocket in self.active_connections.items():
            await websocket.send_json(active_users)

    async def broadcast_message(self, message: str):
        """Broadcast message to all connected clients"""
        message_json = json.loads(message)
        for device_id, websocket in self.active_connections.items():
            await websocket.send_json(
                {
                    "sender": message_json["sender"],
                    "message": message_json["message"],
                    "language": message_json["language"],
                    "type": message_json["type"],
                    "timeStamp": message_json["timeStamp"],
                }
            )

    async def listen_to_server(self):
        """Listen for messages from the server and broadcast them"""
        while True:
            try:
                message = await self.server_socket.recv()
                message_json = json.loads(message)
                print(f"Received message from server: {message_json}")

                if message_json["type"] == "active_users":
                    print(message_json)
                    await self.broadcast_active_users(message_json)

                    # boradcast chat history
                    chat_history = fetch_chat_history()
                    await self.broadcast_chat_history(chat_history)

                else:
                    await self.broadcast_message(message)
            except websockets.ConnectionClosed:
                print("Connection to server closed")
                break

    async def send_message_to_server(
        self,
        sender: str,
        target_device: str,
        message: str,
        language: str,
        timeStamp: str,
        translated_message: str,
    ):
        """Send message to the server"""
        if self.server_socket:
            await self.server_socket.send(
                json.dumps(
                    {
                        "type": "message",
                        "sender": sender,
                        "target_device": target_device,
                        "message": message,
                        "language": language,
                        "timeStamp": timeStamp,
                        "translated_message": translated_message,
                    }
                )
            )
