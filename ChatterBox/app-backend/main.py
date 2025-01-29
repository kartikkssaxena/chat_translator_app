from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import SessionLocal, init_db
from models import Profile, Message
from websocket_manager import WebSocketManager

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

    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()
        print("WebSocket connection closed due to error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)