import os
import json

CHAT_BACKUP_FOLDER = "chat_backups"


def update_chat_history(device_id, chatData: dict):
    target_device = chatData.get("target_device", "")
    if target_device == "server":
        return
    target_device_language = chatData.get("language", "")
    language = chatData.get("language", "")
    chatHistory = chatData.get("chatHistory", [])

    file_path = os.path.join(CHAT_BACKUP_FOLDER, f"{target_device}.json")
    print("chatData", chatData)

    if not os.path.exists(CHAT_BACKUP_FOLDER):
        os.makedirs(CHAT_BACKUP_FOLDER)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            data["device_language"]= language
            data["target_device_language"]= target_device_language,
            data["chatHistory"] = chatHistory.get(target_device, [])
    else:
        data = {
            "device_id": device_id,
            "device_language": language,
            "target_device": target_device,
            "target_device_language": target_device_language,
            "chatHistory": chatHistory,
        }

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def fetch_chat_history():
    consolidated_history = {}
    
    if not os.path.exists(CHAT_BACKUP_FOLDER):
        return consolidated_history
    
    for filename in os.listdir(CHAT_BACKUP_FOLDER):
        if filename.endswith(".json"):
            target_device = filename.replace(".json", "")
            file_path = os.path.join(CHAT_BACKUP_FOLDER, filename)
            
            with open(file_path, "r") as file:
                data = json.load(file)
                consolidated_history[target_device] = data.get("chatHistory", [])
                
    return consolidated_history



