# AI Debate Club

**Github Repository Name Suggestion:** `AI-Debate-Club`

## 專案描述

這是一個桌面應用程式，旨在讓兩個AI大型語言模型（LLM）就使用者指定的主題進行一場有結構的對話或辯論。使用者可以為每個AI設定不同的模型和角色（Persona），觀察它們如何互動、產生見解，並在最後生成對話結論。

本專案採用模組化設計，以便未來輕鬆擴展功能，例如支援更多AI模型API或增加新的輸出格式。

## 核心功能 (v1.45)

- **混合模型對話**: 支援本地 [Ollama](https://ollama.ai/) 模型與雲端 Google Gemini 模型的混合對話。
- **流暢的模型來源切換**: 可為每個AI獨立選擇Ollama或Gemini，切換過程透過背景處理，確保UI介面流暢不卡頓。
- **動態模型選擇**: 對於Ollama，程式會自動偵測本地模型；對於Gemini，提供一組預定義的最新模型列表供選擇。
- **角色管理系統**:
    - **自訂角色庫**: 提供「我的角色庫」管理介面，讓使用者可以新增、編輯、刪除自己的角色，並永久儲存於 `user_personas.json`。
    - **整合下拉式選單**: 使用者的自訂角色會與預設角色一同顯示在下拉選單中，方便快速選用。
- **對話風格管理系統**:
    - **自訂風格庫**: 提供「我的風格庫」管理介面，讓使用者可以新增、編輯、刪除自訂的對話風格指令，並永久儲存於 `user_styles.json`。
    - **快速選用**: 可從下拉選單中快速選用已存檔的風格指令。
- **對話歷史紀錄**:
    - **自動存檔**: 每場對話結束後，會自動將 `.txt` 和 `.json` 兩種格式的紀錄檔儲存至 `history` 資料夾。
    - **歷史紀錄管理**: 提供「對話歷史紀錄」管理介面，可檢視與刪除過去的對話。
- **獨立匯出/匯入**: 支援將「角色庫」與「風格庫」獨立匯出成 `JSON` 檔案進行備份，或從備份檔中匯入。
- **多格式存檔**: 支援將對話紀錄手動儲存為 `.txt`, `.csv`, `.md`, `.docx`(Word), 和 `.xlsx`(Excel) 格式。
- **版本資訊顯示**: UI介面的標題列與右下角狀態列會顯示目前的應用程式版本。
- **修改歷程記錄**: `CHANGELOG.md` 檔案會詳細記錄每個版本的功能變更與修正。

## 如何使用 (預期)

1.  **安裝依賴**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **設定API金鑰 (若要使用Gemini)**:
    - 在專案的根目錄下，建立一個名為 `.env` 的檔案。
    - 在 `.env` 檔案中，加入以下內容，並將 `YOUR_API_KEY` 替換成您自己的 Google Gemini API 金鑰:
      ```
      GEMINI_API_KEY="YOUR_API_KEY"
      ```
    - 應用程式啟動時會自動讀取此金鑰。
3.  **確保Ollama正在運行 (若要使用Ollama)**:
    - 在您的終端機中，確保Ollama服務已經啟動。
4.  **啟動應用程式**:
    ```bash
    python src/app.py
    ```
4.  **設定並開始對話**:
    - 在UI介面中為AI #1和AI #2選擇模型來源與模型。
    - 從下拉選單為它們選擇角色，或在文字框中手動修改。
    - (可選) 輸入對話風格指令。
    - 輸入您感興趣的「對話主題」和「對話回合數」。
    - 點擊「開始對話」。

## 未來規劃 (v2.0+)

- [ ] 支援更多外部API（例如OpenAI）。
- [ ] 儲存和載入自訂的「對話風格指令」。
- [ ] 對話歷史紀錄管理與匯入/匯出。

## Internationalization (i18n)

This project uses `gettext` for internationalization. The UI has been translated into English and Traditional Chinese.

### Managing Translations

If you add or change any user-facing text in the source code (`.py` files), you will need to update the language files.

1.  **Mark strings for translation:** In the Python code, wrap any new user-facing string with the `_()` function. For example: `_("My new string")`.
2.  **Update and compile language files:** Run the helper script from the root directory:
    ```bash
    ./compile_translations.sh
    ```
    This script will automatically find new strings, update the `.po` language files, and compile them into the `.mo` files used by the application.
3.  **Edit translations:** To edit existing translations, modify the `msgstr` fields in the `.po` files located at `src/locales/<language_code>/LC_MESSAGES/messages.po`. After editing, run the `./compile_translations.sh` script again.

### Adding a New Language

1.  Choose the language code (e.g., `fr` for French).
2.  Initialize the new language files by running:
    ```bash
    pybabel init -i src/locales/messages.pot -d src/locales -l fr
    ```
3.  Translate the `msgstr` fields in the newly created `src/locales/fr/LC_MESSAGES/messages.po`.
4.  Add the new language to the language selection menu in `src/ui.py` inside the `_create_menu` method.
5.  Run `./compile_translations.sh` to compile your new language file.
