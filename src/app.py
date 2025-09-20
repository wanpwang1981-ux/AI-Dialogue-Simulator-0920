import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import queue
import json
import os
from datetime import datetime
import gettext
import builtins
from dotenv import load_dotenv

# 匯入我們自己建立的模組
from ui import AppUI, ApiKeyWindow, PersonaManagerWindow, PersonaEditorWindow, StyleManagerWindow, StyleEditorWindow, HistoryManagerWindow
import ollama_client
import gemini_client
import persona_manager
import style_manager
import output_formatter

CONFIG_FILE = "config.json"
APP_VERSION = "1.5.0"

# --- i18n Setup ---
def setup_language(lang_code='zh_TW'):
    """Sets up the application's language."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mo_file_path = os.path.join(script_dir, 'locales', lang_code, 'LC_MESSAGES', 'messages.mo')

        with open(mo_file_path, 'rb') as f:
            lang = gettext.GNUTranslations(f)

        builtins._ = lang.gettext
    except Exception as e:
        # Fallback to a dummy function if any error occurs
        print(f"Warning: Could not load language file for '{lang_code}'. Error: {e}. Falling back to original strings.")
        builtins._ = lambda s: s

def get_language_from_config():
    """Reads the language setting from the config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("language", "zh_TW")
        except (json.JSONDecodeError, IOError):
            return "zh_TW"
    return "zh_TW"
# --- End i18n Setup ---


class MainApp:
    """
    The main application class, responsible for integrating the UI and backend logic.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.geometry("1200x850")

        # The API key is now loaded from .env, so the UI for it is removed.
        commands = {
            "open_persona_manager": self.open_persona_manager_window,
            "open_style_manager": self.open_style_manager_window,
            "open_history": self.open_history_window,
            "save_dialogue": self.save_dialogue,
            "export_personas": lambda: self.export_data("personas"),
            "import_personas": lambda: self.import_data("personas"),
            "export_styles": lambda: self.export_data("styles"),
            "import_styles": lambda: self.import_data("styles"),
            "set_language": self.set_language,
        }

        self.ui = AppUI(root, commands=commands, version=APP_VERSION)
        self.queue = queue.Queue()
        self.conversation_thread = None
        self.stop_event = threading.Event()
        self.structured_log = []
        self.personas = []
        self.styles = []

        # Load language from config and API key from environment
        self.language = get_language_from_config()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        if self.gemini_api_key:
            gemini_client.configure_api_key(self.gemini_api_key)

        self.bind_events()
        self.initialize_app()
        self.process_queue()

    def bind_events(self):
        """Binds all UI events."""
        self.ui.start_button.config(command=self.start_conversation_thread)
        self.ui.stop_button.config(command=self.stop_conversation)
        self.ui.save_button.config(command=self.save_dialogue)
        self.ui.source1_var.trace_add("write", self.on_source_changed)
        self.ui.source2_var.trace_add("write", self.on_source_changed)
        self.ui.persona1_combo.bind("<<ComboboxSelected>>", self.on_persona1_select)
        self.ui.persona2_combo.bind("<<ComboboxSelected>>", self.on_persona2_select)
        self.ui.style_combo.bind("<<ComboboxSelected>>", self.on_style_select)

    def save_config(self):
        """Saves settings (currently just language) to the config file."""
        config_data = {
            "language": self.language
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
        except IOError as e:
            messagebox.showerror(_("Save Settings Failed"), _("Could not write to config file {}: {}").format(CONFIG_FILE, e))

    # --- Persona Management ---
    def open_persona_manager_window(self):
        """Opens the persona management window."""
        self.manager_window = PersonaManagerWindow(self.root)
        self.manager_window.add_button.config(command=self.add_persona)
        self.manager_window.edit_button.config(command=self.edit_persona)
        self.manager_window.delete_button.config(command=self.delete_persona)
        self.refresh_persona_manager_list()

    def refresh_persona_manager_list(self):
        """Refreshes the list in the persona management window."""
        self.manager_window.persona_listbox.delete(0, tk.END)
        user_personas = [p for p in self.personas if not p.get("is_default")]
        for p in user_personas:
            self.manager_window.persona_listbox.insert(tk.END, p["name"])

    def add_persona(self):
        """Opens the add persona window."""
        editor_window = PersonaEditorWindow(self.manager_window)
        editor_window.save_button.config(command=lambda: self.save_new_persona(editor_window))

    def save_new_persona(self, window: PersonaEditorWindow):
        """Saves a new custom persona and refreshes all relevant UI."""
        name = window.name_entry.get().strip()
        prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not name or not prompt:
            messagebox.showwarning(_("Input Error"), _("Persona name and prompt cannot be empty."), parent=window)
            return
        if any(p["name"] == name for p in self.personas):
            messagebox.showwarning(_("Name Conflict"), _("A persona named '{}' already exists.").format(name), parent=window)
            return
        new_persona = {"name": name, "prompt": prompt, "is_default": False}
        self.personas.append(new_persona)
        persona_manager.save_user_personas(self.personas)
        self.refresh_persona_manager_list()
        self.refresh_main_persona_comboboxes()
        window.destroy()

    def edit_persona(self):
        """Opens the edit persona window."""
        selected_indices = self.manager_window.persona_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(_("Nothing Selected"), _("Please select a persona from the list to edit."))
            return
        selected_name = self.manager_window.persona_listbox.get(selected_indices[0])
        persona_to_edit = next((p for p in self.personas if p["name"] == selected_name), None)
        if persona_to_edit:
            editor_window = PersonaEditorWindow(self.manager_window, persona=persona_to_edit)
            editor_window.save_button.config(command=lambda: self.save_edited_persona(editor_window, persona_to_edit))

    def save_edited_persona(self, window: PersonaEditorWindow, old_persona: dict):
        """Saves the edited persona data and refreshes all relevant UI."""
        new_name = window.name_entry.get().strip()
        new_prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not new_name or not new_prompt:
            messagebox.showwarning(_("Input Error"), _("Persona name and prompt cannot be empty."), parent=window)
            return
        if new_name != old_persona["name"] and any(p["name"] == new_name for p in self.personas):
            messagebox.showwarning(_("Name Conflict"), _("A persona named '{}' already exists.").format(new_name), parent=window)
            return
        old_persona["name"] = new_name
        old_persona["prompt"] = new_prompt
        persona_manager.save_user_personas(self.personas)
        self.refresh_persona_manager_list()
        self.refresh_main_persona_comboboxes()
        window.destroy()

    def delete_persona(self):
        """Deletes the selected persona and refreshes all relevant UI."""
        selected_indices = self.manager_window.persona_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(_("Nothing Selected"), _("Please select a persona from the list to delete."))
            return
        selected_name = self.manager_window.persona_listbox.get(selected_indices[0])
        if messagebox.askyesno(_("Confirm Deletion"), _("Are you sure you want to delete the persona '{}'?").format(selected_name)):
            self.personas = [p for p in self.personas if p["name"] != selected_name]
            persona_manager.save_user_personas(self.personas)
            self.refresh_persona_manager_list()
            self.refresh_main_persona_comboboxes()

    # --- Style Management ---
    def open_style_manager_window(self):
        """Opens the style management window."""
        self.style_manager_win = StyleManagerWindow(self.root)
        self.style_manager_win.add_button.config(command=self.add_style)
        self.style_manager_win.edit_button.config(command=self.edit_style)
        self.style_manager_win.delete_button.config(command=self.delete_style)
        self.refresh_style_manager_list()

    def refresh_style_manager_list(self):
        """Refreshes the list in the style management window."""
        self.style_manager_win.style_listbox.delete(0, tk.END)
        for s in self.styles:
            self.style_manager_win.style_listbox.insert(tk.END, s["name"])

    def add_style(self):
        """Opens the add style window."""
        editor = StyleEditorWindow(self.style_manager_win)
        editor.save_button.config(command=lambda: self.save_new_style(editor))

    def save_new_style(self, window: StyleEditorWindow):
        """Saves a new custom style."""
        name = window.name_entry.get().strip()
        prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not name or not prompt:
            messagebox.showwarning(_("Input Error"), _("Style name and prompt cannot be empty."), parent=window)
            return
        if any(s["name"] == name for s in self.styles):
            messagebox.showwarning(_("Name Conflict"), _("A style named '{}' already exists.").format(name), parent=window)
            return
        self.styles.append({"name": name, "prompt": prompt})
        style_manager.save_user_styles(self.styles)
        self.refresh_style_manager_list()
        self.refresh_main_style_combobox()
        window.destroy()

    def edit_style(self):
        """Opens the edit style window."""
        indices = self.style_manager_win.style_listbox.curselection()
        if not indices:
            messagebox.showwarning(_("Nothing Selected"), _("Please select a style to edit."))
            return
        name = self.style_manager_win.style_listbox.get(indices[0])
        style_to_edit = next((s for s in self.styles if s["name"] == name), None)
        if style_to_edit:
            editor = StyleEditorWindow(self.style_manager_win, style=style_to_edit)
            editor.save_button.config(command=lambda: self.save_edited_style(editor, style_to_edit))

    def save_edited_style(self, window: StyleEditorWindow, old_style: dict):
        """Saves an edited style."""
        new_name = window.name_entry.get().strip()
        new_prompt = window.prompt_text.get("1.0", tk.END).strip()
        if not new_name or not new_prompt:
            messagebox.showwarning(_("Input Error"), _("Style name and prompt cannot be empty."), parent=window)
            return
        if new_name != old_style["name"] and any(s["name"] == new_name for s in self.styles):
            messagebox.showwarning(_("Name Conflict"), _("A style named '{}' already exists.").format(new_name), parent=window)
            return
        old_style["name"] = new_name
        old_style["prompt"] = new_prompt
        style_manager.save_user_styles(self.styles)
        self.refresh_style_manager_list()
        self.refresh_main_style_combobox()
        window.destroy()

    def delete_style(self):
        """Deletes the selected style."""
        indices = self.style_manager_win.style_listbox.curselection()
        if not indices:
            messagebox.showwarning(_("Nothing Selected"), _("Please select a style to delete."))
            return
        name = self.style_manager_win.style_listbox.get(indices[0])
        if messagebox.askyesno(_("Confirm Deletion"), _("Are you sure you want to delete the style '{}'?").format(name)):
            self.styles = [s for s in self.styles if s["name"] != name]
            style_manager.save_user_styles(self.styles)
            self.refresh_style_manager_list()
            self.refresh_main_style_combobox()

    # --- Main Application Logic ---
    def initialize_app(self):
        """Initializes the application, loading all data."""
        self.refresh_main_persona_comboboxes()
        self.refresh_main_style_combobox()
        self.on_source_changed()
        self.ui.append_dialogue(_("Please set the parameters and start the dialogue.\n"))

    def refresh_main_persona_comboboxes(self):
        """Refreshes the persona dropdowns in the main window."""
        self.ui.append_dialogue(_("Loading persona list...\n"))
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
            self.ui.append_dialogue(_("Successfully loaded {} personas.\n").format(len(self.personas)))
        else:
            self.ui.append_dialogue(_("Warning: No personas found.\n"))

    def refresh_main_style_combobox(self):
        """Refreshes the style dropdown in the main window."""
        self.styles = style_manager.load_user_styles()
        style_names = [s["name"] for s in self.styles]
        self.ui.style_combo['values'] = style_names

    def on_source_changed(self, var_name=None, index=None, mode=None):
        """Asynchronously updates the model dropdown list when the source changes."""
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
                messagebox.showwarning(
                    _("API Key Missing"),
                    _("You have selected a Gemini model, but no GEMINI_API_KEY was found. Please create a .env file with your key and restart.")
                )
                # Revert the source selection
                if ai_num == 1: self.ui.source1_var.set("Ollama")
                else: self.ui.source2_var.set("Ollama")
                return

            self.update_model_list_for_ai(ai_num, source)

        # Case 2: Called manually (e.g., on init), update both
        else:
            self.update_model_list_for_ai(1, self.ui.source1_var.get())
            self.update_model_list_for_ai(2, self.ui.source2_var.get())

    def update_model_list_for_ai(self, ai_num, source):
        """Updates the model list for a specific AI based on the source."""
        if source == "Ollama":
            threading.Thread(target=self.fetch_ollama_models_thread, args=(ai_num,), daemon=True).start()
        else:
            self.update_combobox(ai_num, gemini_client.SUPPORTED_MODELS)

    def fetch_ollama_models_thread(self, ai_num):
        """(Thread task) Fetches Ollama models and puts them in the queue."""
        models = ollama_client.get_available_models()
        self.queue.put(("update_models", ai_num, models))

    def update_combobox(self, ai_num, models):
        """(Main thread) Updates the specified Combobox."""
        combobox = self.ui.model1_combo if ai_num == 1 else self.ui.model2_combo
        combobox['values'] = models or [_("No models available")]
        combobox.set('')
        combobox.current(0)

    def start_conversation_thread(self):
        """Starts the conversation in a new thread."""
        try:
            settings = self.ui.get_settings()
            if _("No models available") in [settings["model1"], settings["model2"]]:
                 messagebox.showwarning(_("Model Error"), _("Please ensure a valid model is selected."))
                 return
            if ("Gemini" in [settings["source1"], settings["source2"]]) and not self.gemini_api_key:
                messagebox.showerror(_("API Key Error"), _("Before using a Gemini model, please set a valid API key in 'Settings'."))
                return
            self.ui.clear_dialogue()
            self.ui.set_ui_state(is_running=True)
            self.stop_event.clear()
            self.conversation_thread = threading.Thread(target=self.run_conversation_logic, args=(settings,), daemon=True)
            self.conversation_thread.start()
        except Exception as e:
            messagebox.showerror(_("Unknown Error"), _("An error occurred: {}").format(e))
            self.ui.set_ui_state(is_running=False)

    def run_conversation_logic(self, settings):
        """The actual logic for running the conversation. This runs in a separate thread."""
        self.structured_log = []
        persona1_final_prompt = settings["persona1_prompt"]
        persona2_final_prompt = settings["persona2_prompt"]
        if settings["style_prompt"]:
            style_directive = _("\n\n--- Dialogue Style Prompt ---\n{}").format(settings['style_prompt'])
            persona1_final_prompt += style_directive
            persona2_final_prompt += style_directive
        history1 = [{"role": "system", "content": persona1_final_prompt}]
        history2 = [{"role": "system", "content": persona2_final_prompt}]
        header = (_("Character Introduction\n"
                  "Character A: Default Persona({persona1_name})\n"
                  "Prompt:\n{persona1_prompt}\n\n"
                  "Character B: Default Persona({persona2_name})\n"
                  "Prompt:\n{persona2_prompt}\n").format(**settings))
        if settings["style_prompt"]:
            header += _("\nDialogue Style Prompt:\n{}\n").format(settings['style_prompt'])
        header += "==========================================\n"
        self.queue_update(header)
        self.structured_log.append({'speaker': 'System', 'content': header})
        current_message = _("On the topic of: '{}'\nPlease begin the first round of statements on this topic.").format(settings['topic'])
        for i in range(settings['turns'] * 2):
            if self.stop_event.is_set():
                self.queue_update(_("\n--- Dialogue terminated early by user ---\n"))
                break
            turn_number = (i // 2) + 1
            if i % 2 == 0:
                speaker_name = _("Character A: {persona1_name}, Model: {model1}").format(**settings)
                log_speaker_name = _("Character A: {persona1_name}").format(**settings)
                self.queue_update(_("\nRound {turn_number} ({speaker_name}):\n").format(turn_number=turn_number, speaker_name=speaker_name))
                history1.append({"role": "user", "content": current_message})
                response = (ollama_client.generate_response(settings['model1'], history1)
                            if settings['source1'] == 'Ollama'
                            else gemini_client.generate_response(settings['model1'], persona1_final_prompt, history1))
                if response is None:
                    self.queue_update(_("Could not get a response from {}. Dialogue terminated.\n").format(speaker_name))
                    break
                current_message = response
                self.queue_update(f"{current_message}\n")
                self.structured_log.append({'speaker': log_speaker_name, 'content': current_message})
                history1.append({"role": "assistant", "content": current_message})
                history2.append({"role": "user", "content": current_message})
            else:
                speaker_name = _("Character B: {persona2_name}, Model: {model2}").format(**settings)
                log_speaker_name = _("Character B: {persona2_name}").format(**settings)
                self.queue_update(_("\nRound {turn_number} ({speaker_name}):\n").format(turn_number=turn_number, speaker_name=speaker_name))
                history2.append({"role": "user", "content": current_message})
                response = (ollama_client.generate_response(settings['model2'], history2)
                            if settings['source2'] == 'Ollama'
                            else gemini_client.generate_response(settings['model2'], persona2_final_prompt, history2))
                if response is None:
                    self.queue_update(_("Could not get a response from {}. Dialogue terminated.\n").format(speaker_name))
                    break
                current_message = response
                self.queue_update(f"{current_message}\n")
                self.structured_log.append({'speaker': log_speaker_name, 'content': current_message})
                history2.append({"role": "assistant", "content": current_message})
                history1.append({"role": "user", "content": current_message})
        self.queue_update(_("\n--- Dialogue End ---\n"))

    def stop_conversation(self):
        self.ui.append_dialogue(_("\n--- User requested to stop (will take effect after the current turn) ---\n"))
        self.ui.set_ui_state(is_running=False)

    def process_queue(self):
        """Processes messages in the queue, including dialogue content and UI update requests."""
        try:
            while not self.queue.empty():
                message_data = self.queue.get_nowait()
                if isinstance(message_data, str):
                    self.ui.append_dialogue(message_data)
                    # Check for the translated end-of-dialogue strings
                    if _("\n--- Dialogue End ---\n") in message_data or _("\n--- Dialogue terminated early by user ---\n") in message_data:
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
        """Updates the text box content when a style is selected from the dropdown."""
        selected_name = self.ui.style_combo.get()
        if not selected_name: return
        for style in self.styles:
            if style["name"] == selected_name:
                self.ui.style_prompt_text.delete("1.0", tk.END)
                self.ui.style_prompt_text.insert("1.0", style["prompt"])
                break

    # --- History Management ---
    def open_history_window(self):
        """Opens the history management window."""
        self.history_win = HistoryManagerWindow(self.root)
        self.history_win.view_button.config(command=self.view_history)
        self.history_win.delete_button.config(command=self.delete_history)
        self.refresh_history_list()

    def refresh_history_list(self):
        """Refreshes the list in the history window."""
        self.history_win.history_listbox.delete(0, tk.END)
        if not os.path.exists("history"):
            return
        # Read the history folder and sort by filename (time) in descending order
        history_files = sorted([f for f in os.listdir("history") if f.endswith(".txt")], reverse=True)
        for f in history_files:
            self.history_win.history_listbox.insert(tk.END, f)

    def view_history(self):
        """Views the selected history entry."""
        indices = self.history_win.history_listbox.curselection()
        if not indices:
            messagebox.showwarning(_("Nothing Selected"), _("Please select an entry to view."), parent=self.history_win)
            return

        filename = self.history_win.history_listbox.get(indices[0])
        filepath = os.path.join("history", filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.ui.clear_dialogue()
            self.ui.append_dialogue(content)
            self.history_win.destroy() # Close window automatically after viewing
        except Exception as e:
            messagebox.showerror(_("Read Failed"), _("Could not read history file: {}").format(e), parent=self.history_win)

    def delete_history(self):
        """Deletes the selected history entry."""
        indices = self.history_win.history_listbox.curselection()
        if not indices:
            messagebox.showwarning(_("Nothing Selected"), _("Please select an entry to delete."), parent=self.history_win)
            return

        filename_txt = self.history_win.history_listbox.get(indices[0])
        base_filename = os.path.splitext(filename_txt)[0]

        if messagebox.askyesno(_("Confirm Deletion"), _("Are you sure you want to delete the entry '{}'?\n(This will delete both .txt and .json files)").format(base_filename), parent=self.history_win):
            try:
                os.remove(os.path.join("history", filename_txt))
                os.remove(os.path.join("history", base_filename + ".json"))
                self.refresh_history_list() # Refresh list
            except Exception as e:
                messagebox.showerror(_("Delete Failed"), _("Could not delete files: {}").format(e), parent=self.history_win)

    def save_dialogue(self):
        if not self.structured_log:
            messagebox.showwarning(_("No Content"), _("The dialogue history is empty. Nothing to save."))
            return
        file_types = [(_('Word Document'), '*.docx'), (_('Excel Spreadsheet'), '*.xlsx'), (_('CSV files'), '*.csv'), (_('Markdown files'), '*.md'), (_('Text files'), '*.txt'), (_('All files'), '*.*')]
        filepath = filedialog.asksaveasfilename(initialfile=datetime.now().strftime("%Y%m%d%H%M"), filetypes=file_types, defaultextension=".docx", title=_("Save Dialogue History"))
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
            messagebox.showinfo(_("Success"), _("Dialogue successfully saved to:\n{}").format(filepath))
        except Exception as e:
            messagebox.showerror(_("Save Failed"), _("Could not save file: {}").format(e))

    # --- Export/Import Settings ---
    def export_data(self, data_type: str):
        """Exports data of a specified type (personas or styles)."""
        if data_type == "personas":
            data_to_export = [p for p in self.personas if not p.get("is_default")]
            default_filename = "my_personas_backup.json"
            title = _("Export Persona Library")
        elif data_type == "styles":
            data_to_export = self.styles
            default_filename = "my_styles_backup.json"
            title = _("Export Style Library")
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
            messagebox.showinfo(_("Export Successful"), _("Data successfully exported to:\n{}").format(filepath))
        except Exception as e:
            messagebox.showerror(_("Export Failed"), _("Could not save file: {}").format(e))

    def import_data(self, data_type: str):
        """Imports data of a specified type (personas or styles)."""
        if data_type == "personas":
            title = _("Import Persona Library")
        elif data_type == "styles":
            title = _("Import Style Library")
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
            messagebox.showerror(_("Import Failed"), _("Could not read or parse file: {}").format(e))
            return

        title_noun = _("Persona Library") if data_type == "personas" else _("Style Library")
        if messagebox.askyesno(_("Confirm Import"), _("This will overwrite your existing custom {}. Are you sure you want to continue?").format(title_noun)):
            if data_type == "personas":
                self.personas = [p for p in self.personas if p.get("is_default")] + imported_data
                persona_manager.save_user_personas(self.personas)
                self.refresh_main_persona_comboboxes()
            elif data_type == "styles":
                self.styles = imported_data
                style_manager.save_user_styles(self.styles)
                self.refresh_main_style_combobox()

            messagebox.showinfo(_("Import Successful"), _("{} has been successfully imported and applied.").format(title_noun))

    def set_language(self, lang_code: str):
        """Sets the application language and prompts for a restart."""
        if self.language != lang_code:
            self.language = lang_code
            self.save_config()
            messagebox.showinfo(
                _("Language Changed"),
                _("The language has been changed. Please restart the application for the changes to take effect.")
            )

if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()

    # Set up language based on config before creating any UI
    lang_code = get_language_from_config()
    setup_language(lang_code)

    try:
        root = tk.Tk()
        app = MainApp(root)
        root.mainloop()
    except tk.TclError as e:
        print(_("Could not start UI, likely running in a headless environment: {}").format(e))
        print(_("UI startup code skipped."))
    except ImportError as e:
        print(_("Missing module: {}").format(e))
        print(_("Please ensure all dependencies are installed."))
