import asyncio
from fastapi import WebSocket
from src.database.database_manager import DatabaseManager

class ConnectionManager:
    def __init__(self, db_manager: DatabaseManager):
        self.active_connections = {}
        self.db_manager = db_manager

    async def connect(self, websocket: WebSocket, device_id: str):
        """Connect a new client and retrieve chat history"""
        await websocket.accept()
        self.active_connections[device_id] = websocket
        
        # Retrieve device language
        language = self.db_manager.get_device_language(device_id)
        
        # Retrieve and send chat history
        chat_history = self.db_manager.get_chat_history(device_id, device_id)
        for msg in chat_history:
            await websocket.send_json({
                'sender': msg[0],
                'message': msg[1],
                'language': msg[3]
            })
        
        return language

    def disconnect(self, device_id: str):
        """Disconnect a client"""
        if device_id in self.active_connections:
            del self.active_connections[device_id]

    async def send_message(self, sender: str, target_device: str, message: str, language: str):
        """Send message to a specific device"""
        if target_device in self.active_connections:
            target_socket = self.active_connections[target_device]
            await target_socket.send_json({
                'sender': sender,
                'message': message,
                'language': language
            })