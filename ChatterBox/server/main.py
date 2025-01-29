from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Set
import json

app = FastAPI()
active_connections: Dict[str, WebSocket] = {}
active_profiles: Dict[str, dict] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "profile":
                active_profiles[client_id] = {
                    "name": data["name"],
                    "language": data["language"]
                }
                # Broadcast updated profiles to all clients
                await broadcast_profiles()
            elif data["type"] == "message":
                target_id = data["target"]
                if target_id in active_connections:
                    await active_connections[target_id].send_json({
                        "type": "message",
                        "from": client_id,
                        "content": data["content"]
                    })
    except:
        del active_connections[client_id]
        if client_id in active_profiles:
            del active_profiles[client_id]
        await broadcast_profiles()

async def broadcast_profiles():
    """Broadcast active profiles to all connected clients"""
    for connection in active_connections.values():
        await connection.send_json({
            "type": "profiles",
            "profiles": active_profiles
        })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)