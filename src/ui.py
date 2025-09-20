import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

class HistoryManagerWindow(tk.Toplevel):
    """
    一個用於管理對話歷史紀錄的視窗。
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("對話歷史紀錄")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()

        list_frame = ttk.LabelFrame(self, text="已存檔的對話", padding=10)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.history_listbox = tk.Listbox(list_frame, font=("Courier", 10))
        self.history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.view_button = ttk.Button(button_frame, text="檢視")
        self.view_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(button_frame, text="刪除")
        self.delete_button.pack(side="left", padx=5)
        self.close_button = ttk.Button(button_frame, text="關閉", command=self.destroy)
        self.close_button.pack(side="right", padx=5)


class StyleEditorWindow(tk.Toplevel):
    """
    一個用於新增或編輯風格指令的彈出視窗。
    """
    def __init__(self, parent, style=None):
        super().__init__(parent)
        self.title("新增/編輯風格")
        self.geometry("500x450") # 增加預設高度以匹配角色編輯器
        self.transient(parent)
        self.grab_set()

        self.style_data = style

        # 風格名稱
        ttk.Label(self, text="風格名稱:").pack(padx=10, pady=5, anchor="w")
        self.name_entry = ttk.Entry(self, width=50)
        self.name_entry.pack(padx=10, fill="x", expand=True)

        # 風格指令內容
        ttk.Label(self, text="風格指令內容:").pack(padx=10, pady=5, anchor="w")
        self.prompt_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.prompt_text.pack(padx=10, pady=5, fill="both", expand=True)

        if style:
            self.name_entry.insert(0, style.get("name", ""))
            self.prompt_text.insert("1.0", style.get("prompt", ""))

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        self.save_button = ttk.Button(button_frame, text="儲存")
        self.save_button.pack(side="left", padx=5)
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.destroy)
        self.cancel_button.pack(side="left", padx=5)


class StyleManagerWindow(tk.Toplevel):
    """
    一個用於管理使用者自訂風格的視窗。
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("我的風格庫")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        list_frame = ttk.LabelFrame(self, text="自訂風格列表", padding=10)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.style_listbox = tk.Listbox(list_frame)
        self.style_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.style_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.style_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.add_button = ttk.Button(button_frame, text="新增")
        self.add_button.pack(side="left", padx=5)
        self.edit_button = ttk.Button(button_frame, text="編輯")
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(button_frame, text="刪除")
        self.delete_button.pack(side="left", padx=5)
        self.close_button = ttk.Button(button_frame, text="關閉", command=self.destroy)
        self.close_button.pack(side="right", padx=5)


class PersonaEditorWindow(tk.Toplevel):
    """
    一個用於新增或編輯角色的彈出視窗。
    """
    def __init__(self, parent, persona=None):
        super().__init__(parent)
        self.title("新增/編輯角色")
        self.geometry("500x450") # 增加預設高度
        self.transient(parent)
        self.grab_set()

        self.persona_data = persona

        # 角色名稱
        ttk.Label(self, text="角色名稱:").pack(padx=10, pady=5, anchor="w")
        self.name_entry = ttk.Entry(self, width=50)
        self.name_entry.pack(padx=10, fill="x", expand=True)

        # 角色提示詞
        ttk.Label(self, text="角色提示詞 (Persona Prompt):").pack(padx=10, pady=5, anchor="w")
        self.prompt_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.prompt_text.pack(padx=10, pady=5, fill="both", expand=True)

        # 填入現有資料 (如果是編輯模式)
        if persona:
            self.name_entry.insert(0, persona.get("name", ""))
            self.prompt_text.insert("1.0", persona.get("prompt", ""))

        # 按鈕
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        self.save_button = ttk.Button(button_frame, text="儲存") # command將在app.py中綁定
        self.save_button.pack(side="left", padx=5)
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.destroy)
        self.cancel_button.pack(side="left", padx=5)


class PersonaManagerWindow(tk.Toplevel):
    """
    一個用於管理使用者自訂角色的視窗。
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("我的角色庫")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        # 角色列表
        list_frame = ttk.LabelFrame(self, text="自訂角色列表", padding=10)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.persona_listbox = tk.Listbox(list_frame)
        self.persona_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.persona_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.persona_listbox.config(yscrollcommand=scrollbar.set)

        # 按鈕區
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.add_button = ttk.Button(button_frame, text="新增")
        self.add_button.pack(side="left", padx=5)
        self.edit_button = ttk.Button(button_frame, text="編輯")
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(button_frame, text="刪除")
        self.delete_button.pack(side="left", padx=5)
        self.close_button = ttk.Button(button_frame, text="關閉", command=self.destroy)
        self.close_button.pack(side="right", padx=5)


class ApiKeyWindow(tk.Toplevel):
    """
    一個用於輸入和儲存API金鑰的彈出視窗。
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("API 金鑰管理")
        self.geometry("400x150")
        self.transient(parent) # 讓這個視窗保持在父視窗之上
        self.grab_set() # 獨佔輸入焦點

        ttk.Label(self, text="Gemini API Key:").pack(padx=10, pady=5, anchor="w")
        self.api_key_entry = ttk.Entry(self, width=50, show="*")
        self.api_key_entry.pack(padx=10, pady=5, fill="x", expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.save_button = ttk.Button(button_frame, text="儲存")
        self.save_button.pack(side="left", padx=5)
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.destroy)
        self.cancel_button.pack(side="left", padx=5)

class AppUI:
    """
    應用程式的使用者介面 (UI) 層。
    """
    def __init__(self, root: tk.Tk, commands: dict, version=""):
        """
        初始化UI。

        Args:
            root (tk.Tk): Tkinter的主視窗物件。
            commands (dict): 一個包含所有UI命令回呼函式的字典。
            version (str, optional): 要顯示的應用程式版本號。
        """
        self.root = root
        self.root.title(f"AI Debate Club v{version}")
        self.root.geometry("800x850") # 再次增加高度

        self._create_menu(commands)

        # --- 主框架 ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- AI設定區塊 ---
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=5)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)

        # -- AI #1 設定 --
        ai1_frame = ttk.LabelFrame(settings_frame, text="AI #1 設定", padding="10")
        ai1_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # -- 模型來源選擇 --
        source1_frame = ttk.Frame(ai1_frame)
        source1_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(source1_frame, text="模型來源:").pack(side=tk.LEFT, padx=(0, 10))
        self.source1_var = tk.StringVar(value="Ollama")
        self.ollama1_radio = ttk.Radiobutton(source1_frame, text="Ollama (本地)", variable=self.source1_var, value="Ollama")
        self.gemini1_radio = ttk.Radiobutton(source1_frame, text="Gemini (雲端)", variable=self.source1_var, value="Gemini")
        self.ollama1_radio.pack(side=tk.LEFT)
        self.gemini1_radio.pack(side=tk.LEFT, padx=5)

        ttk.Label(ai1_frame, text="選擇模型:").pack(fill=tk.X)
        self.model1_combo = ttk.Combobox(ai1_frame, state="readonly")
        self.model1_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai1_frame, text="預設角色:").pack(fill=tk.X)
        self.persona1_combo = ttk.Combobox(ai1_frame, state="readonly")
        self.persona1_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai1_frame, text="角色提示詞 (可手動修改):").pack(fill=tk.X)
        self.persona1_text = scrolledtext.ScrolledText(ai1_frame, height=5, wrap=tk.WORD)
        self.persona1_text.pack(fill=tk.BOTH, expand=True)

        # -- AI #2 設定 --
        ai2_frame = ttk.LabelFrame(settings_frame, text="AI #2 設定", padding="10")
        ai2_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # -- 模型來源選擇 --
        source2_frame = ttk.Frame(ai2_frame)
        source2_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(source2_frame, text="模型來源:").pack(side=tk.LEFT, padx=(0, 10))
        self.source2_var = tk.StringVar(value="Ollama")
        self.ollama2_radio = ttk.Radiobutton(source2_frame, text="Ollama (本地)", variable=self.source2_var, value="Ollama")
        self.gemini2_radio = ttk.Radiobutton(source2_frame, text="Gemini (雲端)", variable=self.source2_var, value="Gemini")
        self.ollama2_radio.pack(side=tk.LEFT)
        self.gemini2_radio.pack(side=tk.LEFT, padx=5)

        ttk.Label(ai2_frame, text="選擇模型:").pack(fill=tk.X)
        self.model2_combo = ttk.Combobox(ai2_frame, state="readonly")
        self.model2_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai2_frame, text="預設角色:").pack(fill=tk.X)
        self.persona2_combo = ttk.Combobox(ai2_frame, state="readonly")
        self.persona2_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai2_frame, text="角色提示詞 (可手動修改):").pack(fill=tk.X)
        self.persona2_text = scrolledtext.ScrolledText(ai2_frame, height=5, wrap=tk.WORD)
        self.persona2_text.pack(fill=tk.BOTH, expand=True)

        # --- 對話控制區塊 ---
        control_frame = ttk.LabelFrame(main_frame, text="對話設定", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Label(control_frame, text="對話主題:").pack(fill=tk.X)
        self.topic_entry = ttk.Entry(control_frame)
        self.topic_entry.pack(fill=tk.X, pady=(0, 5))
        self.topic_entry.insert(0, "The future of remote work") # 預設主題

        # 新增對話風格指令輸入框
        style_frame = ttk.Frame(control_frame)
        style_frame.pack(fill=tk.X, pady=5)

        ttk.Label(style_frame, text="選擇風格範本:").pack(fill=tk.X)
        self.style_combo = ttk.Combobox(style_frame, state="readonly")
        self.style_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(style_frame, text="對話風格指令 (可選填/手動修改):").pack(fill=tk.X)
        self.style_prompt_text = scrolledtext.ScrolledText(style_frame, height=3, wrap=tk.WORD)
        self.style_prompt_text.pack(fill=tk.BOTH, expand=True)

        control_buttons_frame = ttk.Frame(control_frame)
        control_buttons_frame.pack(fill=tk.X)

        ttk.Label(control_buttons_frame, text="對話回合數:").pack(side=tk.LEFT, padx=(0, 10))
        self.turns_spinbox = ttk.Spinbox(control_buttons_frame, from_=1, to=20, width=5)
        self.turns_spinbox.set("5") # 預設回合數
        self.turns_spinbox.pack(side=tk.LEFT)

        self.start_button = ttk.Button(control_buttons_frame, text="開始對話")
        self.start_button.pack(side=tk.RIGHT)

        self.stop_button = ttk.Button(control_buttons_frame, text="停止對話", state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5)

        # --- 對話紀錄區塊 ---
        dialogue_frame = ttk.LabelFrame(main_frame, text="對話紀錄", padding="10")
        dialogue_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.dialogue_text = scrolledtext.ScrolledText(dialogue_frame, state="disabled", wrap=tk.WORD, height=15)
        self.dialogue_text.pack(fill=tk.BOTH, expand=True)

        # --- 狀態列 ---
        status_frame = ttk.Frame(self.root, padding=(5, 2))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.version_label = ttk.Label(status_frame, text=f"Version: {version}")
        self.version_label.pack(side=tk.RIGHT)

        # --- 存檔區塊 (移到狀態列之上，確保可見) ---
        save_frame = ttk.Frame(self.root, padding=(10, 5))
        save_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.save_button = ttk.Button(save_frame, text="儲存對話紀錄")
        self.save_button.pack(side=tk.RIGHT)

    def set_model_list(self, models: list[str]):
        """設定下拉選單中的模型列表。"""
        self.model1_combo['values'] = models
        self.model2_combo['values'] = models
        if models:
            self.model1_combo.current(0)
            self.model2_combo.current(0)

    def get_settings(self) -> dict:
        """從UI獲取所有設定值。"""
        return {
            "source1": self.source1_var.get(),
            "model1": self.model1_combo.get(),
            "persona1_name": self.persona1_combo.get(),
            "persona1_prompt": self.persona1_text.get("1.0", tk.END).strip(),
            "source2": self.source2_var.get(),
            "model2": self.model2_combo.get(),
            "persona2_name": self.persona2_combo.get(),
            "persona2_prompt": self.persona2_text.get("1.0", tk.END).strip(),
            "topic": self.topic_entry.get().strip(),
            "turns": int(self.turns_spinbox.get()),
            "style_prompt": self.style_prompt_text.get("1.0", tk.END).strip()
        }

    def append_dialogue(self, text: str):
        """將文字附加到對話紀錄區。"""
        self.dialogue_text.config(state="normal")
        self.dialogue_text.insert(tk.END, text)
        self.dialogue_text.config(state="disabled")
        self.dialogue_text.see(tk.END) # 自動捲動到最下方

    def clear_dialogue(self):
        """清空對話紀錄區。"""
        self.dialogue_text.config(state="normal")
        self.dialogue_text.delete("1.0", tk.END)
        self.dialogue_text.config(state="disabled")

    def get_dialogue_content(self) -> str:
        """獲取對話紀錄區的全部內容。"""
        return self.dialogue_text.get("1.0", tk.END)

    def _create_menu(self, commands: dict):
        """建立主選單。"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # 檔案選單
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="檔案", menu=file_menu)
        file_menu.add_command(label="對話歷史紀錄...", command=commands.get("open_history"))
        file_menu.add_command(label="儲存對話紀錄...", command=commands.get("save_dialogue"))
        file_menu.add_separator()

        # 建立一個子選單來處理匯出
        export_menu = tk.Menu(file_menu, tearoff=0)
        export_menu.add_command(label="匯出角色庫...", command=commands.get("export_personas"))
        export_menu.add_command(label="匯出風格庫...", command=commands.get("export_styles"))
        file_menu.add_cascade(label="匯出...", menu=export_menu)

        # 建立一個子選單來處理匯入
        import_menu = tk.Menu(file_menu, tearoff=0)
        import_menu.add_command(label="匯入角色庫...", command=commands.get("import_personas"))
        import_menu.add_command(label="匯入風格庫...", command=commands.get("import_styles"))
        file_menu.add_cascade(label="匯入...", menu=import_menu)

        file_menu.add_separator()
        file_menu.add_command(label="結束", command=self.root.quit)

        # 設定選單
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="設定", menu=settings_menu)
        settings_menu.add_command(label="API金鑰管理", command=commands.get("open_api_key"))
        settings_menu.add_command(label="我的角色庫", command=commands.get("open_persona_manager"))
        settings_menu.add_command(label="我的風格庫", command=commands.get("open_style_manager"))

    def set_ui_state(self, is_running: bool):
        """根據對話是否正在運行來設定UI元件的狀態。"""
        new_state = tk.DISABLED if is_running else tk.NORMAL
        readonly_state = tk.DISABLED if is_running else "readonly"

        # Toggle Buttons
        self.start_button.config(state=tk.NORMAL if not is_running else tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL if is_running else tk.DISABLED)
        self.save_button.config(state=tk.NORMAL if not is_running else tk.DISABLED)

        # Toggle Radio Buttons
        self.ollama1_radio.config(state=new_state)
        self.gemini1_radio.config(state=new_state)
        self.ollama2_radio.config(state=new_state)
        self.gemini2_radio.config(state=new_state)

        # Toggle Comboboxes
        self.model1_combo.config(state=readonly_state)
        self.model2_combo.config(state=readonly_state)
        self.persona1_combo.config(state=readonly_state)
        self.persona2_combo.config(state=readonly_state)
        self.style_combo.config(state=readonly_state)

        # Toggle Text and Entry Fields
        self.persona1_text.config(state=new_state)
        self.persona2_text.config(state=new_state)
        self.style_prompt_text.config(state=new_state)
        self.topic_entry.config(state=new_state)
        self.turns_spinbox.config(state=readonly_state)


# == 用於獨立預覽這個UI檔案 ==
if __name__ == '__main__':
    try:
        root = tk.Tk()
        # 我們需要傳入一個假的 command 來避免錯誤
        app_ui = AppUI(root, api_key_command=lambda: None, persona_manager_command=lambda: None, version="1.42")

        # 加入一些假的模型資料來預覽
        app_ui.set_model_list(["llama3:latest", "gemma:latest", "test-model:7b"])

        # 加入一些假的Persona資料來預覽
        app_ui.persona1_text.insert("1.0", "You are a pragmatic data analyst.")
        app_ui.persona2_text.insert("1.0", "You are a creative and optimistic ideator.")

        root.mainloop()
    except tk.TclError as e:
        print(f"無法啟動UI，可能是在無顯示(headless)環境中運行: {e}")
        print("UI啟動代碼已跳過。")
    except ImportError as e:
        print(f"缺少模組: {e}")
        print("請確保所有依賴都已安裝。")
