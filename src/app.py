import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import queue
import json
import os
from datetime import datetime

# 匯入我們自己建立的模組
from ui import AppUI, ApiKeyWindow, PersonaManagerWindow, PersonaEditorWindow, StyleManagerWindow, StyleEditorWindow, HistoryManagerWindow
import ollama_client
import gemini_client
import persona_manager
import style_manager
import output_formatter

CONFIG_FILE = "config.json"
APP_VERSION = "1.44"

class MainApp:
    """
    主應用程式類別，負責整合UI和後端邏輯。
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.geometry("1200x850")

        commands = {
            "open_api_key": self.open_api_key_window,
            "open_persona_manager": self.open_persona_manager_window,
            "open_style_manager": self.open_style_manager_window,
            "open_history": self.open_history_window,
            "save_dialogue": self.save_dialogue,
            "export_personas": lambda: self.export_data("personas"),
            "import_personas": lambda: self.import_data("personas"),
            "export_styles": lambda: self.export_data("styles"),
            "import_styles": lambda: self.import_data("styles"),
        }

        self.ui = AppUI(root, commands=commands, version=APP_VERSION)
        self.queue = queue.Queue()
        self.conversation_thread = None
        self.stop_event = threading.Event()
        self.structured_log = []
        self.personas = []
        self.styles = []
        self.gemini_api_key = ""

        self.load_config()
        self.bind_events()
        self.initialize_app()
        self.process_queue()

    def bind_events(self):
        """集中綁定所有UI事件。"""
        self.ui.start_button.config(command=self.start_conversation_thread)
        self.ui.stop_button.config(command=self.stop_conversation)
        self.ui.save_button.config(command=self.save_dialogue)
        self.ui.source1_var.trace_add("write", self.on_source_changed)
        self.ui.source2_var.trace_add("write", self.on_source_changed)
        self.ui.persona1_combo.bind("<<ComboboxSelected>>", self.on_persona1_select)
        self.ui.persona2_combo.bind("<<ComboboxSelected>>", self.on_persona2_select)
        self.ui.style_combo.bind("<<ComboboxSelected>>", self.on_style_select)

    def load_config(self):
        """從設定檔載入設定，例如API金鑰。"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.gemini_api_key = config.get("gemini_api_key", "")
                    if self.gemini_api_key:
                        gemini_client.configure_api_key(self.gemini_api_key)
            except (json.JSONDecodeError, IOError): pass

    def save_config(self):
        """儲存設定到設定檔。"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"gemini_api_key": self.gemini_api_key}, f, indent=4)
        except IOError as e:
            messagebox.showerror("儲存設定失敗", f"無法寫入設定檔 {CONFIG_FILE}: {e}")

    # --- API 金鑰管理 ---
    def open_api_key_window(self):
        """打開API金鑰設定視窗。"""
        api_window = ApiKeyWindow(self.root)
        api_window.api_key_entry.insert(0, self.gemini_api_key)
        api_window.save_button.config(command=lambda: self.save_api_key(api_window))

    def save_api_key(self, window: ApiKeyWindow):
        """儲存API金鑰並關閉視窗。"""
        new_key = window.api_key_entry.get().strip()
        if new_key:
            if gemini_client.configure_api_key(new_key):
                self.gemini_api_key = new_key
                self.save_config()
                messagebox.showinfo("成功", "Gemini API 金鑰已儲存並驗證成功。")
                window.destroy()
            else:
                messagebox.showerror("驗證失敗", "此Gemini API 金鑰無效，請重新輸入。", parent=window)
        else:
            messagebox.showwarning("輸入錯誤", "API金鑰不能為空。", parent=window)

    # --- 角色管理 ---
    def open_persona_manager_window(self):
        """打開角色管理視窗。"""
        self.manager_window = PersonaManagerWindow(self.root)
        self.manager_window.add_button.config(command=self.add_persona)
        self.manager_window.edit_button.config(command=self.edit_persona)
        self.manager_window.delete_button.config(command=self.delete_persona)
        self.refresh_persona_manager_list()

    def refresh_persona_manager_list(self):
        """刷新角色管理視窗中的列表。"""
        self.manager_window.persona_listbox.delete(0, tk.END)
        user_personas = [p for p in self.personas if not p.get("is_default")]
        for p in user_personas:
            self.manager_window.persona_listbox.insert(tk.END, p["name"])

    def add_persona(self):
        """打開新增角色視窗。"""
        editor_window = PersonaEditorWindow(self.manager_window)
        editor_window.save_button.config(command=lambda: self.save_new_persona(editor_window))

    def save_new_persona(self, window: PersonaEditorWindow):
        """儲存一個新的自訂角色，並刷新所有相關UI。"""
        name = window.name_entry.get().strip()
        prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not name or not prompt:
            messagebox.showwarning("輸入錯誤", "角色名稱和提示詞不能為空。", parent=window)
            return
        if any(p["name"] == name for p in self.personas):
            messagebox.showwarning("名稱重複", f"名為「{name}」的角色已存在。", parent=window)
            return
        new_persona = {"name": name, "prompt": prompt, "is_default": False}
        self.personas.append(new_persona)
        persona_manager.save_user_personas(self.personas)
        self.refresh_persona_manager_list()
        self.refresh_main_persona_comboboxes()
        window.destroy()

    def edit_persona(self):
        """打開編輯角色視窗。"""
        selected_indices = self.manager_window.persona_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("未選擇", "請先從列表中選擇一個要編輯的角色。")
            return
        selected_name = self.manager_window.persona_listbox.get(selected_indices[0])
        persona_to_edit = next((p for p in self.personas if p["name"] == selected_name), None)
        if persona_to_edit:
            editor_window = PersonaEditorWindow(self.manager_window, persona=persona_to_edit)
            editor_window.save_button.config(command=lambda: self.save_edited_persona(editor_window, persona_to_edit))

    def save_edited_persona(self, window: PersonaEditorWindow, old_persona: dict):
        """儲存被編輯後的角色資料，並刷新所有相關UI。"""
        new_name = window.name_entry.get().strip()
        new_prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not new_name or not new_prompt:
            messagebox.showwarning("輸入錯誤", "角色名稱和提示詞不能為空。", parent=window)
            return
        if new_name != old_persona["name"] and any(p["name"] == new_name for p in self.personas):
            messagebox.showwarning("名稱重複", f"名為「{new_name}」的角色已存在。", parent=window)
            return
        old_persona["name"] = new_name
        old_persona["prompt"] = new_prompt
        persona_manager.save_user_personas(self.personas)
        self.refresh_persona_manager_list()
        self.refresh_main_persona_comboboxes()
        window.destroy()

    def delete_persona(self):
        """刪除選定的角色，並刷新所有相關UI。"""
        selected_indices = self.manager_window.persona_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("未選擇", "請先從列表中選擇一個要刪除的角色。")
            return
        selected_name = self.manager_window.persona_listbox.get(selected_indices[0])
        if messagebox.askyesno("確認刪除", f"您確定要刪除角色「{selected_name}」嗎？"):
            self.personas = [p for p in self.personas if p["name"] != selected_name]
            persona_manager.save_user_personas(self.personas)
            self.refresh_persona_manager_list()
            self.refresh_main_persona_comboboxes()

    # --- 風格管理 ---
    def open_style_manager_window(self):
        self.style_manager_win = StyleManagerWindow(self.root)
        self.style_manager_win.add_button.config(command=self.add_style)
        self.style_manager_win.edit_button.config(command=self.edit_style)
        self.style_manager_win.delete_button.config(command=self.delete_style)
        self.refresh_style_manager_list()

    def refresh_style_manager_list(self):
        self.style_manager_win.style_listbox.delete(0, tk.END)
        for s in self.styles:
            self.style_manager_win.style_listbox.insert(tk.END, s["name"])

    def add_style(self):
        editor = StyleEditorWindow(self.style_manager_win)
        editor.save_button.config(command=lambda: self.save_new_style(editor))

    def save_new_style(self, window: StyleEditorWindow):
        name = window.name_entry.get().strip()
        prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not name or not prompt:
            messagebox.showwarning("輸入錯誤", "風格名稱和指令不能為空。", parent=window)
            return
        if any(s["name"] == name for s in self.styles):
            messagebox.showwarning("名稱重複", f"名為「{name}」的風格已存在。", parent=window)
            return
        self.styles.append({"name": name, "prompt": prompt})
        style_manager.save_user_styles(self.styles)
        self.refresh_style_manager_list()
        self.refresh_main_style_combobox()
        window.destroy()

    def edit_style(self):
        indices = self.style_manager_win.style_listbox.curselection()
        if not indices:
            messagebox.showwarning("未選擇", "請先選擇一個要編輯的風格。")
            return
        name = self.style_manager_win.style_listbox.get(indices[0])
        style_to_edit = next((s for s in self.styles if s["name"] == name), None)
        if style_to_edit:
            editor = StyleEditorWindow(self.style_manager_win, style=style_to_edit)
            editor.save_button.config(command=lambda: self.save_edited_style(editor, style_to_edit))

    def save_edited_style(self, window: StyleEditorWindow, old_style: dict):
        new_name = window.name_entry.get().strip()
        new_prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not new_name or not new_prompt:
            messagebox.showwarning("輸入錯誤", "風格名稱和指令不能為空。", parent=window)
            return
        if new_name != old_style["name"] and any(s["name"] == new_name for s in self.styles):
            messagebox.showwarning("名稱重複", f"名為「{new_name}」的風格已存在。", parent=window)
            return
        old_style["name"] = new_name
        old_style["prompt"] = new_prompt
        style_manager.save_user_styles(self.styles)
        self.refresh_style_manager_list()
        self.refresh_main_style_combobox()
        window.destroy()

    def delete_style(self):
        indices = self.style_manager_win.style_listbox.curselection()
        if not indices:
            messagebox.showwarning("未選擇", "請先選擇一個要刪除的風格。")
            return
        name = self.style_manager_win.style_listbox.get(indices[0])
        if messagebox.askyesno("確認刪除", f"您確定要刪除風格「{name}」嗎？"):
            self.styles = [s for s in self.styles if s["name"] != name]
            style_manager.save_user_styles(self.styles)
            self.refresh_style_manager_list()
            self.refresh_main_style_combobox()

    # --- 主應用邏輯 ---
    def initialize_app(self):
        """初始化應用程式，載入所有資料。"""
        self.refresh_main_persona_comboboxes()
        self.refresh_main_style_combobox()
        self.on_source_changed()
        self.ui.append_dialogue("請設定參數並開始對話。\n")

    def refresh_main_persona_comboboxes(self):
        """刷新主視窗的角色下拉選單。"""
        self.ui.append_dialogue("正在載入角色列表...\n")
        self.personas = persona_manager.get_all_personas()
        if self.personas:
            persona_names = [p["name"] for p in self.personas]
            self.ui.persona1_combo['values'] = persona_names
            self.ui.persona2_combo['values'] = persona_names
            if len(self.personas) >= 2:
                self.ui.persona1_combo.current(0)
                self.ui.persona2_combo.current(1)
            elif len(self.personas) == 1:
                self.ui.persona1_combo.current(0)
                self.ui.persona2_combo.current(0)
            self.on_persona1_select()
            self.on_persona2_select()
            self.ui.append_dialogue(f"成功載入 {len(self.personas)} 個角色。\n")
        else:
            self.ui.append_dialogue("警告：找不到任何角色。\n")

    def refresh_main_style_combobox(self):
        """刷新主視窗的風格下拉選單。"""
        self.styles = style_manager.load_user_styles()
        style_names = [s["name"] for s in self.styles]
        self.ui.style_combo['values'] = style_names

    def on_source_changed(self, var_name=None, index=None, mode=None):
        """當模型來源改變時，非同步更新對應的模型下拉列表。"""
        # Case 1: Called by a trace (user action), update only the changed AI
        if var_name:
            if var_name == str(self.ui.source1_var):
                ai_num = 1
                source = self.ui.source1_var.get()
            elif var_name == str(self.ui.source2_var):
                ai_num = 2
                source = self.ui.source2_var.get()
            else:
                return # Not a source variable we care about

            if source == "Gemini" and not self.gemini_api_key:
                messagebox.showinfo("需要設定", "您選擇了Gemini模型，請先設定您的API金鑰。")
                self.open_api_key_window()
                if not self.gemini_api_key: # Revert if no key was entered
                    if ai_num == 1: self.ui.source1_var.set("Ollama")
                    else: self.ui.source2_var.set("Ollama")
                    return

            self.update_model_list_for_ai(ai_num, source)

        # Case 2: Called manually (e.g., on init), update both
        else:
            source1 = self.ui.source1_var.get()
            source2 = self.ui.source2_var.get()
            if (source1 == "Gemini" or source2 == "Gemini") and not self.gemini_api_key:
                 # In init, we don't need to pop up the window, just proceed
                 pass
            self.update_model_list_for_ai(1, source1)
            self.update_model_list_for_ai(2, source2)

    def update_model_list_for_ai(self, ai_num, source):
        """根據來源更新指定AI的模型列表。"""
        if source == "Ollama":
            threading.Thread(target=self.fetch_ollama_models_thread, args=(ai_num,), daemon=True).start()
        else:
            self.update_combobox(ai_num, gemini_client.SUPPORTED_MODELS)

    def fetch_ollama_models_thread(self, ai_num):
        """(執行緒工作) 獲取Ollama模型並放入佇列。"""
        models = ollama_client.get_available_models()
        self.queue.put(("update_models", ai_num, models))

    def update_combobox(self, ai_num, models):
        """(主執行緒) 更新指定的Combobox。"""
        combobox = self.ui.model1_combo if ai_num == 1 else self.ui.model2_combo
        combobox['values'] = models or ["無可用模型"]
        combobox.set('')
        combobox.current(0)

    def start_conversation_thread(self):
        """在一個新的執行緒中開始對話。"""
        try:
            settings = self.ui.get_settings()
            if "無可用模型" in [settings["model1"], settings["model2"]]:
                 messagebox.showwarning("模型錯誤", "請確保選擇了可用的模型。")
                 return
            if ("Gemini" in [settings["source1"], settings["source2"]]) and not self.gemini_api_key:
                messagebox.showerror("API金鑰錯誤", "使用Gemini模型前，請先在「設定」中設定有效的API金鑰。")
                return
            self.ui.clear_dialogue()
            self.ui.set_ui_state(is_running=True)
            self.stop_event.clear()
            self.conversation_thread = threading.Thread(target=self.run_conversation_logic, args=(settings,), daemon=True)
            self.conversation_thread.start()
        except Exception as e:
            messagebox.showerror("未知錯誤", f"發生錯誤: {e}")
            self.ui.set_ui_state(is_running=False)

    def run_conversation_logic(self, settings):
        """實際執行對話的邏輯。這個函式在一個單獨的執行緒中運行。"""
        self.structured_log = []
        persona1_final_prompt = settings["persona1_prompt"]
        persona2_final_prompt = settings["persona2_prompt"]
        if settings["style_prompt"]:
            style_directive = f"\n\n--- 對話風格指令 ---\n{settings['style_prompt']}"
            persona1_final_prompt += style_directive
            persona2_final_prompt += style_directive
        history1 = [{"role": "system", "content": persona1_final_prompt}]
        history2 = [{"role": "system", "content": persona2_final_prompt}]
        header = (f"角色介紹\n"
                  f"角色A：預設角色({settings['persona1_name']})\n"
                  f"提示詞：\n{settings['persona1_prompt']}\n\n"
                  f"角色B：預設角色({settings['persona2_name']})\n"
                  f"提示詞：\n{settings['persona2_prompt']}\n")
        if settings["style_prompt"]:
            header += f"\n對話風格指令：\n{settings['style_prompt']}\n"
        header += "==========================================\n"
        self.queue_update(header)
        self.structured_log.append({'speaker': 'System', 'content': header})
        current_message = f"關於主題： '{settings['topic']}'\n請您針對此主題，開始進行第一回合的發言。"
        for i in range(settings['turns'] * 2):
            if self.stop_event.is_set():
                self.queue_update("\n--- 對話被使用者提前終止 ---\n")
                break
            turn_number = (i // 2) + 1
            if i % 2 == 0:
                speaker_name = f"角色A：{settings['persona1_name']},模型：{settings['model1']}"
                log_speaker_name = f"角色A：{settings['persona1_name']}"
                self.queue_update(f"\n第{turn_number}回合對話 ({speaker_name}):\n")
                history1.append({"role": "user", "content": current_message})
                response = (ollama_client.generate_response(settings['model1'], history1)
                            if settings['source1'] == 'Ollama'
                            else gemini_client.generate_response(settings['model1'], persona1_final_prompt, history1))
                if response is None:
                    self.queue_update(f"無法從 {speaker_name} 獲取回應，對話終止。\n")
                    break
                current_message = response
                self.queue_update(f"{current_message}\n")
                self.structured_log.append({'speaker': log_speaker_name, 'content': current_message})
                history1.append({"role": "assistant", "content": current_message})
                history2.append({"role": "user", "content": current_message})
            else:
                speaker_name = f"角色B：{settings['persona2_name']},模型：{settings['model2']}"
                log_speaker_name = f"角色B：{settings['persona2_name']}"
                self.queue_update(f"\n第{turn_number}回合對話 ({speaker_name}):\n")
                history2.append({"role": "user", "content": current_message})
                response = (ollama_client.generate_response(settings['model2'], history2)
                            if settings['source2'] == 'Ollama'
                            else gemini_client.generate_response(settings['model2'], persona2_final_prompt, history2))
                if response is None:
                    self.queue_update(f"無法從 {speaker_name} 獲取回應，對話終止。\n")
                    break
                current_message = response
                self.queue_update(f"{current_message}\n")
                self.structured_log.append({'speaker': log_speaker_name, 'content': current_message})
                history2.append({"role": "assistant", "content": current_message})
                history1.append({"role": "user", "content": current_message})
        self.queue_update("\n--- 對話結束 ---\n")

    def stop_conversation(self):
        self.ui.append_dialogue("\n--- 使用者請求停止（將在目前回合結束後生效） ---\n")
        self.ui.set_ui_state(is_running=False)

    def process_queue(self):
        """處理佇列中的訊息，包括對話內容和UI更新請求。"""
        try:
            while not self.queue.empty():
                message_data = self.queue.get_nowait()
                if isinstance(message_data, str):
                    self.ui.append_dialogue(message_data)
                    if "--- 對話結束 ---" in message_data or "--- 對話被使用者提前終止 ---" in message_data:
                        self.ui.set_ui_state(is_running=False)
                elif isinstance(message_data, tuple):
                    msg_type, ai_num, data = message_data
                    if msg_type == "update_models":
                        self.update_combobox(ai_num, data)
        finally:
            self.root.after(100, self.process_queue)

    def queue_update(self, message: str):
        self.queue.put(message)

    def on_persona1_select(self, event=None):
        selected_name = self.ui.persona1_combo.get()
        if not selected_name: return
        for persona in self.personas:
            if persona["name"] == selected_name:
                self.ui.persona1_text.delete("1.0", tk.END)
                self.ui.persona1_text.insert("1.0", persona["prompt"])
                break

    def on_persona2_select(self, event=None):
        selected_name = self.ui.persona2_combo.get()
        if not selected_name: return
        for persona in self.personas:
            if persona["name"] == selected_name:
                self.ui.persona2_text.delete("1.0", tk.END)
                self.ui.persona2_text.insert("1.0", persona["prompt"])
                break

    def on_style_select(self, event=None):
        """當風格下拉選單被選擇時，更新文字框內容。"""
        selected_name = self.ui.style_combo.get()
        if not selected_name: return
        for style in self.styles:
            if style["name"] == selected_name:
                self.ui.style_prompt_text.delete("1.0", tk.END)
                self.ui.style_prompt_text.insert("1.0", style["prompt"])
                break

    # --- 歷史紀錄管理 ---
    def open_history_window(self):
        """打開歷史紀錄管理視窗。"""
        self.history_win = HistoryManagerWindow(self.root)
        self.history_win.view_button.config(command=self.view_history)
        self.history_win.delete_button.config(command=self.delete_history)
        self.refresh_history_list()

    def refresh_history_list(self):
        """刷新歷史紀錄視窗的列表。"""
        self.history_win.history_listbox.delete(0, tk.END)
        if not os.path.exists("history"):
            return
        # 讀取history資料夾，並按檔名(時間)倒序排序
        history_files = sorted([f for f in os.listdir("history") if f.endswith(".txt")], reverse=True)
        for f in history_files:
            self.history_win.history_listbox.insert(tk.END, f)

    def view_history(self):
        """檢視選定的歷史紀錄。"""
        indices = self.history_win.history_listbox.curselection()
        if not indices:
            messagebox.showwarning("未選擇", "請先選擇一筆要檢視的紀錄。", parent=self.history_win)
            return

        filename = self.history_win.history_listbox.get(indices[0])
        filepath = os.path.join("history", filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.ui.clear_dialogue()
            self.ui.append_dialogue(content)
            self.history_win.destroy() # 檢視後自動關閉視窗
        except Exception as e:
            messagebox.showerror("讀取失敗", f"無法讀取歷史紀錄檔案: {e}", parent=self.history_win)

    def delete_history(self):
        """刪除選定的歷史紀錄。"""
        indices = self.history_win.history_listbox.curselection()
        if not indices:
            messagebox.showwarning("未選擇", "請先選擇一筆要刪除的紀錄。", parent=self.history_win)
            return

        filename_txt = self.history_win.history_listbox.get(indices[0])
        base_filename = os.path.splitext(filename_txt)[0]

        if messagebox.askyesno("確認刪除", f"您確定要刪除紀錄「{base_filename}」嗎？\n(將會同時刪除 .txt 和 .json 檔案)", parent=self.history_win):
            try:
                os.remove(os.path.join("history", filename_txt))
                os.remove(os.path.join("history", base_filename + ".json"))
                self.refresh_history_list() # 刷新列表
            except Exception as e:
                messagebox.showerror("刪除失敗", f"無法刪除檔案: {e}", parent=self.history_win)

    def save_dialogue(self):
        if not self.structured_log:
            messagebox.showwarning("沒有內容", "對話紀錄是空的，沒有什麼可以儲存。")
            return
        file_types = [('Word Document', '*.docx'), ('Excel Spreadsheet', '*.xlsx'), ('CSV files', '*.csv'), ('Markdown files', '*.md'), ('Text files', '*.txt'), ('All files', '*.*')]
        filepath = filedialog.asksaveasfilename(initialfile=datetime.now().strftime("%Y%m%d%H%M"), filetypes=file_types, defaultextension=".docx", title="儲存對話紀錄")
        if not filepath:
            return
        file_ext = os.path.splitext(filepath)[1].lower()
        try:
            if file_ext == ".xlsx":
                output_formatter.to_xlsx(self.structured_log, filepath)
            elif file_ext == ".docx":
                output_formatter.to_docx(self.structured_log, filepath)
            else:
                if file_ext == ".csv":
                    content_to_save = output_formatter.to_csv(self.structured_log)
                elif file_ext == ".md":
                    content_to_save = output_formatter.to_md(self.structured_log)
                else:
                    content_to_save = output_formatter.to_txt(self.structured_log)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content_to_save)
            messagebox.showinfo("成功", f"對話已成功儲存到:\n{filepath}")
        except Exception as e:
            messagebox.showerror("儲存失敗", f"無法儲存檔案: {e}")

    # --- 匯出/匯入設定 ---
    def export_data(self, data_type: str):
        """匯出指定類型的資料 (personas 或 styles)。"""
        if data_type == "personas":
            data_to_export = [p for p in self.personas if not p.get("is_default")]
            default_filename = "my_personas_backup.json"
            title = "匯出角色庫"
        elif data_type == "styles":
            data_to_export = self.styles
            default_filename = "my_styles_backup.json"
            title = "匯出風格庫"
        else:
            return

        filepath = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title=title
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_to_export, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("匯出成功", f"資料已成功匯出至:\n{filepath}")
        except Exception as e:
            messagebox.showerror("匯出失敗", f"無法儲存檔案: {e}")

    def import_data(self, data_type: str):
        """匯入指定類型的資料 (personas 或 styles)。"""
        if data_type == "personas":
            title = "匯入角色庫"
        elif data_type == "styles":
            title = "匯入風格庫"
        else:
            return

        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=title
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
        except Exception as e:
            messagebox.showerror("匯入失敗", f"無法讀取或解析檔案: {e}")
            return

        if messagebox.askyesno("確認匯入", f"這將會覆蓋您現有的自訂{title.replace('匯入', '')}。您確定要繼續嗎？"):
            if data_type == "personas":
                self.personas = [p for p in self.personas if p.get("is_default")] + imported_data
                persona_manager.save_user_personas(self.personas)
                self.refresh_main_persona_comboboxes()
            elif data_type == "styles":
                self.styles = imported_data
                style_manager.save_user_styles(self.styles)
                self.refresh_main_style_combobox()

            messagebox.showinfo("匯入成功", f"{title.replace('匯入', '')}已成功匯入並應用。")

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = MainApp(root)
        root.mainloop()
    except tk.TclError as e:
        print(f"無法啟動UI，可能是在無顯示(headless)環境中運行: {e}")
        print("UI啟動代碼已跳過。")
    except ImportError as e:
        print(f"缺少模組: {e}")
        print("請確保所有依賴都已安裝。")
