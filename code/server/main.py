import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.database.database_manager import DatabaseManager
from src.websocket.connection_manager import ConnectionManager

# Create database and connection managers
db_manager = DatabaseManager()
connection_manager = ConnectionManager(db_manager)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/server")
async def websocket_endpoint(websocket: WebSocket):

    language = await connection_manager.connect(websocket)

    try:
        while True:
            # Receive message from backend
            data = await websocket.receive_json()
            print(f"server - Received message from backend")
            print(f"server - Data: {data}")
            target_device = data["target_device"]
            await connection_manager.send_message(data, target_device)

    except WebSocketDisconnect:
        connection_manager.disconnect("server")


def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8770)


if __name__ == "__main__":
    run_server()
