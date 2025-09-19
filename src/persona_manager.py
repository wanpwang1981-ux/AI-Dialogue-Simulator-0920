from typing import List, Dict, Optional
import os
import json

DEFAULT_PERSONAS_FILE = "DEFAULT_PERSONAS.md"
USER_PERSONAS_FILE = "user_personas.json"

def load_default_personas() -> List[Dict[str, str]]:
    """
    解析Markdown檔案，提取預設的AI角色。
    """
    personas = []
    if not os.path.exists(DEFAULT_PERSONAS_FILE):
        return personas

    try:
        with open(DEFAULT_PERSONAS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        persona_blocks = content.split('---')

        for block in persona_blocks:
            block = block.strip()
            if not block or "### 角色：" not in block:
                continue

            lines = block.split('\n')
            name_line = lines[0]

            try:
                name = name_line.split('：')[1].split('(')[0].strip()
            except IndexError:
                continue

            prompt = "\n".join(lines[1:]).strip()
            personas.append({"name": f"[預設] {name}", "prompt": prompt, "is_default": True})

    except Exception as e:
        print(f"錯誤: 解析預設角色檔案時發生錯誤: {e}")

    return personas

def load_user_personas() -> List[Dict[str, str]]:
    """
    從JSON檔案載入使用者自訂的角色。
    """
    if not os.path.exists(USER_PERSONAS_FILE):
        return []
    try:
        with open(USER_PERSONAS_FILE, 'r', encoding='utf-8') as f:
            user_personas = json.load(f)
            for p in user_personas:
                p["is_default"] = False
            return user_personas
    except (json.JSONDecodeError, IOError) as e:
        print(f"錯誤: 讀取使用者角色檔案時發生錯誤: {e}")
        return []

def save_user_personas(personas: List[Dict[str, str]]):
    """
    將使用者自訂的角色儲存到JSON檔案。
    """
    user_only_personas = [
        {"name": p["name"], "prompt": p["prompt"]} for p in personas if not p.get("is_default")
    ]
    try:
        with open(USER_PERSONAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_only_personas, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"錯誤: 儲存使用者角色檔案時發生錯誤: {e}")

def get_all_personas() -> List[Dict[str, str]]:
    """
    獲取所有角色（預設+使用者自訂）。
    """
    default = load_default_personas()
    user = load_user_personas()
    return default + user
