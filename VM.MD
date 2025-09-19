# 虛擬環境與設定指南 (VM & Setup Guide)

本文件提供在您自己的電腦上設定和執行 "AI Debate Club" 應用程式的詳細步驟。雖然檔名為 `VM.MD`，但您不需要一個完整的虛擬機器(Virtual Machine)，只需要一個乾淨的Python環境即可。

## 1. 先決條件 (Prerequisites)

- **Python 3.8 或更新版本**: 請確保您的系統已安裝Python。您可以從 [python.org](https://www.python.org/downloads/) 下載。
- **Git**: 用於複製本專案的程式碼。

## 2. 步驟一：取得專案程式碼

打開您的終端機或命令提示字元，並使用`git`複製本專案的儲存庫：

```bash
git clone <repository-url>
cd AI-Debate-Club
```
*（請將 `<repository-url>` 替換為實際的Git儲存庫網址）*

## 3. 步驟二：建立Python虛擬環境 (強烈建議)

為了避免與您系統上其他的Python專案產生依賴衝突，建議為本專案建立一個獨立的虛擬環境。

```bash
# 建立一個名為 .venv 的虛擬環境
python -m venv .venv

# 啟動虛擬環境
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```
啟動後，您應該會在終端機的提示符號前看到 `(.venv)` 的字樣。

## 4. 步驟三：安裝必要的依賴套件

本專案的所有依賴都記錄在 `requirements.txt` 檔案中。在已啟動的虛擬環境中，執行以下指令進行安裝：

```bash
pip install -r requirements.txt
```

## 5. 步驟四：設定模型後端 (Ollama) (選用)

如果您想使用本地的大型語言模型，您需要安裝並執行 [Ollama](https://ollama.ai/)。

1.  前往 [Ollama 官網](https://ollama.ai/) 下載並安裝適合您作業系統的版本。
2.  安裝完成後，開啟終端機並拉取您想使用的模型。例如，拉取Llama 3：
    ```bash
    ollama pull llama3
    ```
3.  **在執行主應用程式之前，請確保Ollama服務正在背景執行中。**

## 6. 步驟五：設定API金鑰 (選用)

如果您想使用 `Gemini` 或 `OpenAI` 的雲端模型，您需要取得對應的API金鑰。

1.  **Gemini API Key**: 前往 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得您的金鑰。
2.  **OpenAI API Key**: 前往 [OpenAI Platform](https://platform.openai.com/api-keys) 取得您的金鑰。

取得金鑰後，您可以在啟動應用程式後，點擊頂部選單的「設定」->「API金鑰管理」來輸入並儲存它們。

## 7. 步驟六：執行應用程式

完成以上所有步驟後，您可以執行以下指令來啟動 "AI Debate Club"：

```bash
python src/app.py
```

現在，您應該能看到應用程式的主視窗了！開始設定您的第一場AI辯論吧！
