import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3
from datetime import datetime
import os

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for chat storage"""
        os.makedirs('chat_backups', exist_ok=True)
        self.conn = sqlite3.connect('chat_database.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Use parameterized datetime storage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                message TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def save_message(self, sender, receiver, message):
        """Save message to database"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        res = cursor.execute('''
            INSERT INTO messages 
            (sender, receiver, message, timestamp) 
            VALUES (?, ?, ?, ?)
        ''', (sender, receiver, message, timestamp))
        print(f"Message saved: {sender} -> {receiver}: {message}")
        print(f"Message ID: {res}")
        self.conn.commit()

    def get_chat_history(self, sender, receiver):
        """Retrieve chat history between two devices"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT sender, message, timestamp 
            FROM messages 
            WHERE (sender = ? AND receiver = ?) OR 
                  (sender = ? AND receiver = ?)
            ORDER BY timestamp
        ''', (sender, receiver, receiver, sender))
        return cursor.fetchall()

    async def connect(self, websocket: WebSocket, device_id: str):
        """Connect a new client"""
        await websocket.accept()
        self.active_connections[device_id] = websocket
        
        # Retrieve and send chat history
        chat_history = self.get_chat_history(device_id, device_id)
        print
        for msg in chat_history:
            await websocket.send_json({
                'sender': msg[0],
                'message': msg[1]
            })
        
        print(f"Device {device_id} connected")

    def disconnect(self, device_id: str):
        """Disconnect a client"""
        if device_id in self.active_connections:
            del self.active_connections[device_id]
        print(f"Device {device_id} disconnected")

    async def send_message(self, sender: str, target_device: str, message: str):
        """Send message to a specific device"""
        if target_device in self.active_connections:
            target_socket = self.active_connections[target_device]
            await target_socket.send_json({
                'sender': sender,
                'message': message
            })

# Create FastAPI app and connection manager
app = FastAPI()
manager = ConnectionManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await manager.connect(websocket, device_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            target_device = data['target_device']
            message = data['message']

            # Save message to database
            manager.save_message(
                sender=device_id, 
                receiver=target_device, 
                message=message
            )

            # Send message to target device
            await manager.send_message(device_id, target_device, message)

    except WebSocketDisconnect:
        manager.disconnect(device_id)

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8765)

if __name__ == "__main__":
    run_server()