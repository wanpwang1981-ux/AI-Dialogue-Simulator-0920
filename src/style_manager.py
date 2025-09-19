from typing import List, Dict
import os
import json

USER_STYLES_FILE = "user_styles.json"

def load_user_styles() -> List[Dict[str, str]]:
    """
    從JSON檔案載入使用者自訂的對話風格。
    """
    if not os.path.exists(USER_STYLES_FILE):
        return []
    try:
        with open(USER_STYLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"錯誤: 讀取使用者風格檔案時發生錯誤: {e}")
        return []

def save_user_styles(styles: List[Dict[str, str]]):
    """
    將使用者自訂的風格儲存到JSON檔案。
    """
    try:
        with open(USER_STYLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(styles, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"錯誤: 儲存使用者風格檔案時發生錯誤: {e}")

# == 用於獨立測試這個模組的範例 ==
if __name__ == '__main__':
    print("--- 測試風格管理器 ---")

    # 建立一個假的風格列表來測試儲存
    mock_styles = [
        {"name": "嚴肅辯論", "prompt": "請你們用非常嚴肅、正式的語氣進行辯論，並引用數據佐證。"},
        {"name": "輕鬆閒聊", "prompt": "請你們用輕鬆、口語化的方式閒聊，可以互相開玩笑。"}
    ]

    print("\n正在測試儲存功能 (將建立 user_styles.json)...")
    save_user_styles(mock_styles)

    if os.path.exists(USER_STYLES_FILE):
        print("   user_styles.json 建立成功。")

        print("\n正在測試重新載入使用者風格...")
        reloaded_styles = load_user_styles()
        print(f"   成功從檔案載入 {len(reloaded_styles)} 個風格。")
        if len(reloaded_styles) == 2 and reloaded_styles[0]['name'] == '嚴肅辯論':
            print("   資料驗證成功。")
        else:
            print("   資料驗證失敗！")

        # 清理測試檔案
        os.remove(USER_STYLES_FILE)
        print("\n已清理測試檔案 user_styles.json。")

    else:
        print("   儲存失敗！")

    print("\n--- 測試完成 ---")
