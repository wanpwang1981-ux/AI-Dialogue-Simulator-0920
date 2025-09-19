import google.generativeai as genai
from typing import List, Dict, Optional

# 使用者指定的Gemini模型列表 (使用官方API ID)
SUPPORTED_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

def configure_api_key(api_key: str) -> bool:
    """
    設定Google Gemini API金鑰。

    Args:
        api_key (str): 使用者的API金鑰。

    Returns:
        bool: 如果金鑰被設定則返回True，否則False。
    """
    if not api_key:
        return False
    try:
        genai.configure(api_key=api_key)
        # 嘗試列出模型以驗證金鑰是否有效
        genai.list_models()
        return True
    except Exception as e:
        print(f"錯誤: 設定Gemini API金鑰時發生問題: {e}")
        return False

def generate_response(
    model_name: str,
    system_prompt: str,
    conversation_history: List[Dict[str, str]]
) -> Optional[str]:
    """
    使用指定的Gemini模型生成一個新的回應。

    Args:
        model_name (str): 要使用的模型名稱 (例如, "gemini-1.5-flash")。
        system_prompt (str): AI的系統提示詞/角色設定。
        conversation_history (List[Dict[str, str]]): 對話歷史記錄。
            Gemini的格式與Ollama稍有不同，它需要 'user' 和 'model' 角色。

    Returns:
        Optional[str]: AI生成的回應內容。如果發生錯誤則返回None。
    """
    if model_name not in SUPPORTED_MODELS:
        print(f"錯誤: 不支援的模型 '{model_name}'。")
        return None

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )

        # 將Ollama格式 ('user'/'assistant') 轉換為Gemini格式 ('user'/'model')
        gemini_history = []
        for message in conversation_history:
            role = 'user' if message['role'] == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [message['content']]})

        # 從歷史紀錄中找到最後一個 'user' 的訊息來發送
        if gemini_history and gemini_history[-1]['role'] == 'user':
            last_user_prompt = gemini_history[-1]['parts'][0]
            # 建立一個帶有先前歷史的對話
            chat = model.start_chat(history=gemini_history[:-1])
            response = chat.send_message(last_user_prompt)
            return response.text
        else:
            print("錯誤: 對話歷史的最後一則訊息不是來自使用者。")
            return None

    except Exception as e:
        print(f"錯誤: Gemini API請求失敗: {e}")
        return f"Gemini API 錯誤: {e}"
