from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import SessionLocal, init_db
from models import Profile, Message
from websocket_manager import WebSocketManager
import asyncio
import websockets
import json

app = FastAPI()
ws_manager = WebSocketManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.websocket("/ws/connect")
async def connect(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted")

    try:
        while True:
            data = await websocket.receive_json()
            print("Received data:", data)
            profile = Profile(name=data["name"], language=data["language"])
            print("Created profile:", profile)

            db = SessionLocal()
            db.add(profile)
            db.commit()
            print("Profile saved to database")

            await ws_manager.connect(websocket, profile)
            print("WebSocketManager connected")
            await websocket.send_json({"status": 200})
            print("Sent status 200 to client")

            # Connect to the server using the profile name as the device ID
            await connect_to_server(profile.name)

    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
        print("WebSocket connection closed due to error")

async def connect_to_server(device_id: str):
    print(f"Connecting to server with device ID: {device_id}")
    uri = f"ws://localhost:8765/ws/{device_id}"

    async with websockets.connect(uri) as websocket:
        # Send profile information to the server
        await websocket.send(json.dumps({
            "type": "profile",
            "name": device_id,
            "language": "English"  # Replace with actual language if needed
        }))
        print(f"Connected to server with device ID: {device_id}")

        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received message from server: {data}")
                # Handle incoming messages from the server
                if data["type"] == "message":
                    # Process the message as needed
                    print(f"Message from {data['from']}: {data['content']}")
        except websockets.ConnectionClosed as e:
            print(f"Connection to server closed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)