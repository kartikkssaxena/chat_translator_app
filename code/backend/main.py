import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.database.database_manager import DatabaseManager
from src.websocket.connection_manager import ConnectionManager
from src.chat_history.chat_backup_handler import update_chat_history

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

@app.on_event("startup")
async def startup_event():
    await connection_manager.connect_to_server("ws://192.168.1.178:8770/ws/server")

@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    # Get device language on connection
    language = await connection_manager.connect(websocket, device_id)
    
    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_json()
            target_device = data['target_device']
            message = data['message']
            new_language  = data.get('language', language)
            chatHistory = data.get('chatHistory', [])
            timeStamp = data.get('timeStamp', '')
            translated_message = data.get('translated_message', '')

            print("backend")
            print(f"Received message from frontend", data)

            # Save device language if changed
            if new_language  != language:
                db_manager.save_device_language(device_id, new_language )
                language = new_language 

            # Ensure chat_backups folder exists
            if not os.path.exists('chat_backups'):
                os.makedirs('chat_backups')
            update_chat_history (device_id, data)

            # before this we have received the message from the frontend
            # saved the chat history and language prefernce of the user
            
            # this is where we can add the chat translator bit.
            # set the translated message variable

            # now we are sending data to server
            print("sending data to server")
            # Forward message to the server
            await connection_manager.send_message_to_server(
                device_id, 
                target_device, 
                message, 
                language,
                timeStamp,
                translated_message
            )

    except WebSocketDisconnect:
        connection_manager.disconnect(device_id)

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8765)

if __name__ == "__main__":
    run_server()