import requests
import time

# Configuration
MODEL_NAME = "llama3"
OLLAMA_URL = "http://localhost:11434"
API_ENDPOINT = f"{OLLAMA_URL}/api/generate"


def send_message(prompt: str, language: str) -> str:
    """
    Send a message to Ollama and return the response.

    Args:
        prompt (str): User input message

    Returns:
        str: Response from the model
    """
    # language = "french"
    prompt = "Translate the following text in "+ language + ", text: " + prompt + ".Return ONLY the translated text."
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    try:
        # Increase timeout for model inference and add connection timeout
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=(10, 300),  # (connection_timeout, read_timeout)
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response received")
        else:
            return f"Error: HTTP {response.status_code} - {response.text}"

    except requests.exceptions.ConnectTimeout:
        return "❌ Connection timeout - Cannot reach Ollama service"
    except requests.exceptions.ReadTimeout:
        return "⏱️ Response timeout - Model is taking too long. Try a shorter prompt or different model."
    except requests.RequestException as e:
        return f"Connection error: {str(e)}"



# def main():
#     start_time = time.time()
#     print("🤖 Thinking...")
#     response = send_message("Hi my name is kartik, what is your name ?")
#     end_time = time.time()
#     elapsed = end_time - start_time
#     print(f"Bot: {response}\n")
#     print(f"⚡ Completed in {elapsed:.2f}s\n")


# if __name__ == "__main__":
#     main()
