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

@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    # Get device language on connection
    language = await connection_manager.connect(websocket, device_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            target_device = data['target_device']
            message = data['message']
            new_language = data.get('language', language)

            # Save device language if changed
            if new_language != language:
                db_manager.save_device_language(device_id, new_language)
                language = new_language

            # Save message to database
            db_manager.save_message(
                sender=device_id, 
                receiver=target_device, 
                message=message,
                language=language
            )

            # Send message to target device
            await connection_manager.send_message(
                device_id, 
                target_device, 
                message, 
                language
            )

    except WebSocketDisconnect:
        connection_manager.disconnect(device_id)

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8765)

if __name__ == "__main__":
    run_server()