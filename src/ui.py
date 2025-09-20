import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

# This is a dummy assignment for pybabel to recognize the _ function.
# The actual translation function is injected into builtins by app.py.
_ = lambda s: s

class HistoryManagerWindow(tk.Toplevel):
    """
    A window for managing conversation history.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("Dialogue History"))
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()

        list_frame = ttk.LabelFrame(self, text=_("Saved Conversations"), padding=10)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.history_listbox = tk.Listbox(list_frame, font=("Courier", 10))
        self.history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.view_button = ttk.Button(button_frame, text=_("View"))
        self.view_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(button_frame, text=_("Delete"))
        self.delete_button.pack(side="left", padx=5)
        self.close_button = ttk.Button(button_frame, text=_("Close"), command=self.destroy)
        self.close_button.pack(side="right", padx=5)


class StyleEditorWindow(tk.Toplevel):
    """
    A popup window for adding or editing style prompts.
    """
    def __init__(self, parent, style=None):
        super().__init__(parent)
        self.title(_("Add/Edit Style"))
        self.geometry("500x450") # Increase default height to match persona editor
        self.transient(parent)
        self.grab_set()

        self.style_data = style

        # Style Name
        ttk.Label(self, text=_("Style Name:")).pack(padx=10, pady=5, anchor="w")
        self.name_entry = ttk.Entry(self, width=50)
        self.name_entry.pack(padx=10, fill="x", expand=True)

        # Style Prompt Content
        ttk.Label(self, text=_("Style Prompt Content:")).pack(padx=10, pady=5, anchor="w")
        self.prompt_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.prompt_text.pack(padx=10, pady=5, fill="both", expand=True)

        if style:
            self.name_entry.insert(0, style.get("name", ""))
            self.prompt_text.insert("1.0", style.get("prompt", ""))

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        self.save_button = ttk.Button(button_frame, text=_("Save"))
        self.save_button.pack(side="left", padx=5)
        self.cancel_button = ttk.Button(button_frame, text=_("Cancel"), command=self.destroy)
        self.cancel_button.pack(side="left", padx=5)


class StyleManagerWindow(tk.Toplevel):
    """
    A window for managing user-defined styles.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("My Styles"))
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        list_frame = ttk.LabelFrame(self, text=_("Custom Styles List"), padding=10)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.style_listbox = tk.Listbox(list_frame)
        self.style_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.style_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.style_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.add_button = ttk.Button(button_frame, text=_("Add"))
        self.add_button.pack(side="left", padx=5)
        self.edit_button = ttk.Button(button_frame, text=_("Edit"))
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(button_frame, text=_("Delete"))
        self.delete_button.pack(side="left", padx=5)
        self.close_button = ttk.Button(button_frame, text=_("Close"), command=self.destroy)
        self.close_button.pack(side="right", padx=5)


class PersonaEditorWindow(tk.Toplevel):
    """
    A popup window for adding or editing personas.
    """
    def __init__(self, parent, persona=None):
        super().__init__(parent)
        self.title(_("Add/Edit Persona"))
        self.geometry("500x450") # Increase default height
        self.transient(parent)
        self.grab_set()

        self.persona_data = persona

        # Persona Name
        ttk.Label(self, text=_("Persona Name:")).pack(padx=10, pady=5, anchor="w")
        self.name_entry = ttk.Entry(self, width=50)
        self.name_entry.pack(padx=10, fill="x", expand=True)

        # Persona Prompt
        ttk.Label(self, text=_("Persona Prompt:")).pack(padx=10, pady=5, anchor="w")
        self.prompt_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.prompt_text.pack(padx=10, pady=5, fill="both", expand=True)

        # Fill with existing data (if in edit mode)
        if persona:
            self.name_entry.insert(0, persona.get("name", ""))
            self.prompt_text.insert("1.0", persona.get("prompt", ""))

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        self.save_button = ttk.Button(button_frame, text=_("Save")) # command will be bound in app.py
        self.save_button.pack(side="left", padx=5)
        self.cancel_button = ttk.Button(button_frame, text=_("Cancel"), command=self.destroy)
        self.cancel_button.pack(side="left", padx=5)


class PersonaManagerWindow(tk.Toplevel):
    """
    A window for managing user-defined personas.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("My Personas"))
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        # Persona List
        list_frame = ttk.LabelFrame(self, text=_("Custom Personas List"), padding=10)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.persona_listbox = tk.Listbox(list_frame)
        self.persona_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.persona_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.persona_listbox.config(yscrollcommand=scrollbar.set)

        # Button Area
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.add_button = ttk.Button(button_frame, text=_("Add"))
        self.add_button.pack(side="left", padx=5)
        self.edit_button = ttk.Button(button_frame, text=_("Edit"))
        self.edit_button.pack(side="left", padx=5)
        self.delete_button = ttk.Button(button_frame, text=_("Delete"))
        self.delete_button.pack(side="left", padx=5)
        self.close_button = ttk.Button(button_frame, text=_("Close"), command=self.destroy)
        self.close_button.pack(side="right", padx=5)


class ApiKeyWindow(tk.Toplevel):
    """
    A popup window for entering and saving the API key.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("API Key Management"))
        self.geometry("400x150")
        self.transient(parent) # Keep this window on top of its parent
        self.grab_set() # Grab all input focus

        ttk.Label(self, text=_("Gemini API Key:")).pack(padx=10, pady=5, anchor="w")
        self.api_key_entry = ttk.Entry(self, width=50, show="*")
        self.api_key_entry.pack(padx=10, pady=5, fill="x", expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.save_button = ttk.Button(button_frame, text=_("Save"))
        self.save_button.pack(side="left", padx=5)
        self.cancel_button = ttk.Button(button_frame, text=_("Cancel"), command=self.destroy)
        self.cancel_button.pack(side="left", padx=5)

class AppUI:
    """
    The user interface (UI) layer of the application.
    """
    def __init__(self, root: tk.Tk, commands: dict, version=""):
        """
        Initializes the UI.

        Args:
            root (tk.Tk): The main Tkinter window object.
            commands (dict): A dictionary containing all UI command callback functions.
            version (str, optional): The application version number to display.
        """
        self.root = root
        self.root.title(_("AI Debate Club v{}").format(version))
        self.root.geometry("800x850") # Increased height again

        self._create_menu(commands)

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- AI Settings Block ---
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=5)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)

        # -- AI #1 Settings --
        ai1_frame = ttk.LabelFrame(settings_frame, text=_("AI #1 Settings"), padding="10")
        ai1_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # -- Model Source Selection --
        source1_frame = ttk.Frame(ai1_frame)
        source1_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(source1_frame, text=_("Model Source:")).pack(side=tk.LEFT, padx=(0, 10))
        self.source1_var = tk.StringVar(value="Ollama")
        self.ollama1_radio = ttk.Radiobutton(source1_frame, text=_("Ollama (Local)"), variable=self.source1_var, value="Ollama")
        self.gemini1_radio = ttk.Radiobutton(source1_frame, text=_("Gemini (Cloud)"), variable=self.source1_var, value="Gemini")
        self.ollama1_radio.pack(side=tk.LEFT)
        self.gemini1_radio.pack(side=tk.LEFT, padx=5)

        ttk.Label(ai1_frame, text=_("Select Model:")).pack(fill=tk.X)
        self.model1_combo = ttk.Combobox(ai1_frame, state="readonly")
        self.model1_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai1_frame, text=_("Default Persona:")).pack(fill=tk.X)
        self.persona1_combo = ttk.Combobox(ai1_frame, state="readonly")
        self.persona1_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai1_frame, text=_("Persona Prompt (can be manually edited):")).pack(fill=tk.X)
        self.persona1_text = scrolledtext.ScrolledText(ai1_frame, height=5, wrap=tk.WORD)
        self.persona1_text.pack(fill=tk.BOTH, expand=True)

        # -- AI #2 Settings --
        ai2_frame = ttk.LabelFrame(settings_frame, text=_("AI #2 Settings"), padding="10")
        ai2_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # -- Model Source Selection --
        source2_frame = ttk.Frame(ai2_frame)
        source2_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(source2_frame, text=_("Model Source:")).pack(side=tk.LEFT, padx=(0, 10))
        self.source2_var = tk.StringVar(value="Ollama")
        self.ollama2_radio = ttk.Radiobutton(source2_frame, text=_("Ollama (Local)"), variable=self.source2_var, value="Ollama")
        self.gemini2_radio = ttk.Radiobutton(source2_frame, text=_("Gemini (Cloud)"), variable=self.source2_var, value="Gemini")
        self.ollama2_radio.pack(side=tk.LEFT)
        self.gemini2_radio.pack(side=tk.LEFT, padx=5)

        ttk.Label(ai2_frame, text=_("Select Model:")).pack(fill=tk.X)
        self.model2_combo = ttk.Combobox(ai2_frame, state="readonly")
        self.model2_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai2_frame, text=_("Default Persona:")).pack(fill=tk.X)
        self.persona2_combo = ttk.Combobox(ai2_frame, state="readonly")
        self.persona2_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai2_frame, text=_("Persona Prompt (can be manually edited):")).pack(fill=tk.X)
        self.persona2_text = scrolledtext.ScrolledText(ai2_frame, height=5, wrap=tk.WORD)
        self.persona2_text.pack(fill=tk.BOTH, expand=True)

        # --- Dialogue Control Block ---
        control_frame = ttk.LabelFrame(main_frame, text=_("Dialogue Settings"), padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Label(control_frame, text=_("Dialogue Topic:")).pack(fill=tk.X)
        self.topic_entry = ttk.Entry(control_frame)
        self.topic_entry.pack(fill=tk.X, pady=(0, 5))
        self.topic_entry.insert(0, "The future of remote work") # Default topic

        # New dialogue style prompt input box
        style_frame = ttk.Frame(control_frame)
        style_frame.pack(fill=tk.X, pady=5)

        ttk.Label(style_frame, text=_("Select Style Template:")).pack(fill=tk.X)
        self.style_combo = ttk.Combobox(style_frame, state="readonly")
        self.style_combo.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(style_frame, text=_("Dialogue Style Prompt (optional/editable):")).pack(fill=tk.X)
        self.style_prompt_text = scrolledtext.ScrolledText(style_frame, height=3, wrap=tk.WORD)
        self.style_prompt_text.pack(fill=tk.BOTH, expand=True)

        control_buttons_frame = ttk.Frame(control_frame)
        control_buttons_frame.pack(fill=tk.X)

        ttk.Label(control_buttons_frame, text=_("Number of Turns:")).pack(side=tk.LEFT, padx=(0, 10))
        self.turns_spinbox = ttk.Spinbox(control_buttons_frame, from_=1, to=20, width=5)
        self.turns_spinbox.set("5") # Default turns
        self.turns_spinbox.pack(side=tk.LEFT)

        self.start_button = ttk.Button(control_buttons_frame, text=_("Start Dialogue"))
        self.start_button.pack(side=tk.RIGHT)

        self.stop_button = ttk.Button(control_buttons_frame, text=_("Stop Dialogue"), state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5)

        # --- Dialogue History Block ---
        dialogue_frame = ttk.LabelFrame(main_frame, text=_("Dialogue History"), padding="10")
        dialogue_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.dialogue_text = scrolledtext.ScrolledText(dialogue_frame, state="disabled", wrap=tk.WORD, height=15)
        self.dialogue_text.pack(fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        status_frame = ttk.Frame(self.root, padding=(5, 2))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.version_label = ttk.Label(status_frame, text=_("Version: {}").format(version))
        self.version_label.pack(side=tk.RIGHT)

        # --- Save Block (moved above status bar for visibility) ---
        save_frame = ttk.Frame(self.root, padding=(10, 5))
        save_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.save_button = ttk.Button(save_frame, text=_("Save Dialogue History..."))
        self.save_button.pack(side=tk.RIGHT)

    def set_model_list(self, models: list[str]):
        """Sets the list of models in the dropdowns."""
        self.model1_combo['values'] = models
        self.model2_combo['values'] = models
        if models:
            self.model1_combo.current(0)
            self.model2_combo.current(0)

    def get_settings(self) -> dict:
        """Gets all settings from the UI."""
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
        """Appends text to the dialogue history area."""
        self.dialogue_text.config(state="normal")
        self.dialogue_text.insert(tk.END, text)
        self.dialogue_text.config(state="disabled")
        self.dialogue_text.see(tk.END) # Auto-scroll to the bottom

    def clear_dialogue(self):
        """Clears the dialogue history area."""
        self.dialogue_text.config(state="normal")
        self.dialogue_text.delete("1.0", tk.END)
        self.dialogue_text.config(state="disabled")

    def get_dialogue_content(self) -> str:
        """Gets the entire content of the dialogue history area."""
        return self.dialogue_text.get("1.0", tk.END)

    def _create_menu(self, commands: dict):
        """Creates the main menu."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=_("File"), menu=file_menu)
        file_menu.add_command(label=_("Dialogue History..."), command=commands.get("open_history"))
        file_menu.add_command(label=_("Save Dialogue History..."), command=commands.get("save_dialogue"))
        file_menu.add_separator()

        # Create a submenu for Export
        export_menu = tk.Menu(file_menu, tearoff=0)
        export_menu.add_command(label=_("Export Personas..."), command=commands.get("export_personas"))
        export_menu.add_command(label=_("Export Styles..."), command=commands.get("export_styles"))
        file_menu.add_cascade(label=_("Export..."), menu=export_menu)

        # Create a submenu for Import
        import_menu = tk.Menu(file_menu, tearoff=0)
        import_menu.add_command(label=_("Import Personas..."), command=commands.get("import_personas"))
        import_menu.add_command(label=_("Import Styles..."), command=commands.get("import_styles"))
        file_menu.add_cascade(label=_("Import..."), menu=import_menu)

        file_menu.add_separator()
        file_menu.add_command(label=_("Exit"), command=self.root.quit)

        # Settings Menu
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=_("Settings"), menu=settings_menu)
        settings_menu.add_command(label=_("API Key Management"), command=commands.get("open_api_key"))
        settings_menu.add_command(label=_("My Personas"), command=commands.get("open_persona_manager"))
        settings_menu.add_command(label=_("My Styles"), command=commands.get("open_style_manager"))

        settings_menu.add_separator()
        language_menu = tk.Menu(settings_menu, tearoff=0)
        language_menu.add_command(label="English", command=lambda: commands.get("set_language")("en"))
        language_menu.add_command(label="繁體中文", command=lambda: commands.get("set_language")("zh_TW"))
        settings_menu.add_cascade(label=_("Language"), menu=language_menu)

    def set_ui_state(self, is_running: bool):
        """Sets the state of UI elements based on whether a conversation is running."""
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


# == For standalone preview of this UI file ==
if __name__ == '__main__':
    # Dummy setup for gettext for standalone preview
    import builtins
    builtins._ = lambda s: s.format() if '{}' in s else s

    try:
        root = tk.Tk()
        # We need to pass a dummy commands dict to avoid errors
        app_ui = AppUI(root, commands={}, version="1.42-preview")

        # Add some fake model data for preview
        app_ui.set_model_list(["llama3:latest", "gemma:latest", "test-model:7b"])

        # Add some fake Persona data for preview
        app_ui.persona1_text.insert("1.0", "You are a pragmatic data analyst.")
        app_ui.persona2_text.insert("1.0", "You are a creative and optimistic ideator.")

        root.mainloop()
    except tk.TclError as e:
        print(f"Could not start UI, likely running in a headless environment: {e}")
        print("UI startup code skipped.")
    except ImportError as e:
        print(f"Missing module: {e}")
        print("Please ensure all dependencies are installed.")
