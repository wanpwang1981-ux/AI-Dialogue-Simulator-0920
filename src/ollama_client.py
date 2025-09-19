import requests
import json
from typing import List, Dict, Any

# Ollama API的預設基礎URL
OLLAMA_BASE_URL = "http://localhost:11434"

def get_available_models(base_url: str = OLLAMA_BASE_URL) -> List[str]:
    """
    從Ollama API獲取所有可用的模型列表。

    Args:
        base_url (str): Ollama服務的基礎URL。

    Returns:
        List[str]: 可用模型名稱的列表。如果發生錯誤則返回空列表。
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        # 如果請求失敗，拋出HTTPError異常
        response.raise_for_status()
        models_data = response.json().get("models", [])
        # 從返回的列表中提取模型名稱
        return [model["name"] for model in models_data]
    except requests.exceptions.RequestException as e:
        # 捕獲所有requests相關的異常 (例如，連線錯誤)
        print(f"Error connecting to Ollama at {base_url}: {e}")
        return []
    except json.JSONDecodeError:
        # 捕獲JSON解析錯誤
        print(f"Error: Failed to decode JSON response from Ollama.")
        return []

def generate_response(
    model_name: str,
    conversation_history: List[Dict[str, str]],
    base_url: str = OLLAMA_BASE_URL
) -> str | None:
    """
    使用指定的模型和對話歷史，向Ollama API請求生成一個新的回應。

    Args:
        model_name (str): 要使用的模型名稱 (例如, "llama3:latest")。
        conversation_history (List[Dict[str, str]]): 對話歷史記錄，
            格式為 [{"role": "user", "content": "..."}, ...]。
        base_url (str): Ollama服務的基礎URL。

    Returns:
        str | None: AI生成的回應內容。如果發生錯誤則返回None。
    """
    try:
        payload = {
            "model": model_name,
            "messages": conversation_history,
            "stream": False  # 為簡化起見，我們不使用流式傳輸
        }
        response = requests.post(f"{base_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        response_data = response.json()

        # 檢查回應中是否包含預期的 'message' 和 'content'
        if "message" in response_data and "content" in response_data["message"]:
            return response_data["message"]["content"]
        else:
            print(f"Error: Unexpected response format from Ollama: {response_data}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during Ollama generation request: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON response from Ollama.")
        return None
