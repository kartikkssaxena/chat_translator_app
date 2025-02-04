import asyncio
import websockets
from fastapi import WebSocket
from src.database.database_manager import DatabaseManager
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

    async def connect_to_server(self, server_url: str):
        """Connect to the server and start listening for messages"""
        self.server_socket = await websockets.connect(server_url)
        asyncio.create_task(self.listen_to_server())

    async def listen_to_server(self):
        """Listen for messages from the server and print them"""
        while True:
            try:
                message = await self.server_socket.recv()
                print(f"Received message from server: {message}")
            except websockets.ConnectionClosed:
                print("Connection to server closed")
                break

    async def send_message_to_server(self, sender: str, target_device: str, message: str, language: str):
        """Send message to the server"""
        if self.server_socket:
            await self.server_socket.send(
                json.dumps({
                    'sender': sender,
                    'target_device': target_device,
                    'message': message,
                    'language': language
                })
            )