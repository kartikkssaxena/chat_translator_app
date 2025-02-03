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

    conn_res = await connection_manager.connect(websocket)
    print("/n" + (conn_res) + "/n")

    try:
        while True:
            # Receive message from backend
            data = await websocket.receive_json()
            print(f"server - Received message from backend")
            print(f"server - Data: {data}")
            device_id = data["sender"]
            target_device = data["target_device"]
            message = data["message"]
            new_language = data.get("language", language)

            print(f"server - Received message from {device_id} to {target_device}")
            print(f"server - Message: {message}")
            print(f"server - Language: {new_language}")

            # Save device language if changed
            if new_language != language:
                db_manager.save_device_language(device_id, new_language)
                language = new_language

            # Save message to database
            db_manager.save_message(
                sender=device_id,
                receiver=target_device,
                message=message,
                language=language,
            )

            # sending data to target device
            # Forward message to target backend
            await connection_manager.send_message(
                device_id, target_device, message, language
            )

    except WebSocketDisconnect:
        connection_manager.disconnect("server")


def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8770)


if __name__ == "__main__":
    run_server()
