import tkinter as tk
from tkinter import ttk
from translations import get_text

class LanguageSelector:
    def __init__(self, parent, speech_window):
        self.parent = parent
        self.speech_window = speech_window
        self.window = None

        # There are many more supported languages, i just added some of them for now.
        self.languages = {
            "Türkçe": "tr",
            "English (US)": "en",
            "English (UK)": "en-GB",
            "Deutsch": "de",
            "Français": "fr",
            "Español": "es",
            "Italiano": "it",
            "Português": "pt",
            "Русский": "ru",
            "中文": "zh",
            "日本語": "ja",
            "한국어": "ko",
        }
        
        # Auto-match STT language with app language
        self.set_language_from_app()
        
    def set_language_from_app(self):
        """Set STT language to match current app language"""
        app_language = self.parent.current_language
        
        if app_language == "tr":
            self.selected_language_key = "Türkçe"
            self.language = "tr"
        elif app_language == "en":
            self.selected_language_key = "English (US)"
            self.language = "en"
        else:
            # Default to English if unknown language
            self.selected_language_key = "English (US)"
            self.language = "en"
        
    def show_language_selector(self):
        if self.window is not None:
            self.window.focus()
            return
            
        self.window = tk.Toplevel(self.parent.root)
        self.window.title(get_text("language_selector_title", self.parent.current_language))
        self.window.geometry("300x400")
        self.window.resizable(False, False)
        
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 300) // 2
        y = (self.window.winfo_screenheight() - 400) // 2
        self.window.geometry(f"300x400+{x}+{y}")
        
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.main_frame, text=get_text("select_speech_language", self.parent.current_language), 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        listbox_frame = ttk.Frame(self.main_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.language_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        self.language_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.language_listbox.yview)
        
        languages = list(self.languages.keys())
        for lang in languages:
            self.language_listbox.insert(tk.END, lang)
            
        current_lang_code = self.languages[self.selected_language_key]
        for i, (lang_name, lang_code) in enumerate(self.languages.items()):
            if lang_code == current_lang_code:
                self.language_listbox.selection_set(i)
                self.language_listbox.see(i)
                break
        
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text=get_text("select_button", self.parent.current_language), command=self.select_language).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text=get_text("cancel_button", self.parent.current_language), command=self.close_window).pack(side=tk.RIGHT)
        
        self.language_listbox.bind("<Double-Button-1>", lambda e: self.select_language())
        
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
    def select_language(self):
        selection = self.language_listbox.curselection()
        if selection:
            selected_lang_key = self.language_listbox.get(selection[0])
            self.language = self.languages[selected_lang_key]
            self.selected_language_key = selected_lang_key
            self.speech_window.lang_choice_btn.config(text=selected_lang_key)
        self.close_window()
        
    def close_window(self):
        if self.window:
            self.window.destroy()
            self.window = None

class SpeechToTextWindow:
    def __init__(self, parent, api_key, save_api_btn):
        self.parent = parent
        self.save_api_btn = save_api_btn
        self.api_key = api_key
        self.window = None
        self.is_recording = False
        self.audio_processor = None
        self.ws = None
        self.stream = None
        self.p = None
        self.language_selector = LanguageSelector(parent, self)
        self.mic_devices = []
        self.selected_mic_index = None
        
        self.result_text = ""
    
    def update_api_key(self, api_key):
        self.api_key = api_key
        
    def create_window(self):
        if self.window is not None:
            return

        self.window = tk.Toplevel()
        self.window.title(get_text("speech_window_title", self.parent.current_language))
        self.window_width, self.window_height = 450, 260
        self.window.geometry(f"{self.window_width}x{self.window_height}")
        self.window.resizable(False, False)

        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = screen_height - self.window_height
        self.window.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        self.window.attributes("-topmost", True)
        self.window.attributes("-toolwindow", True)

        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        lang_frame = ttk.Frame(self.main_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(lang_frame, text=get_text("language_choice", self.parent.current_language) + ":").pack(side=tk.LEFT)
        self.lang_choice_btn = ttk.Button(lang_frame, text=self.language_selector.selected_language_key, 
                  command=self.language_selector.show_language_selector)
        self.lang_choice_btn.pack(side=tk.LEFT, padx=(5, 0))

        mic_sel_frame = ttk.Frame(self.main_frame)
        mic_sel_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(mic_sel_frame, text=get_text("microphone_selection", self.parent.current_language)).pack(side=tk.LEFT)
        import pyaudio
        p = pyaudio.PyAudio()
        self.mic_devices = []
        mic_names = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                self.mic_devices.append({'index': i, 'name': info['name']})
                mic_names.append(f"[{i}] {info['name']}")
        if not self.mic_devices:
            mic_names = ["Varsayılan (Bulunamadı)"]
            self.selected_mic_index = None
        else:
            self.selected_mic_index = self.mic_devices[0]['index']
        self.mic_combo = ttk.Combobox(mic_sel_frame, values=mic_names, state="readonly")
        self.mic_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.mic_combo.current(0)
        def on_mic_select(event=None):
            sel = self.mic_combo.current()
            if sel >= 0 and sel < len(self.mic_devices):
                self.selected_mic_index = self.mic_devices[sel]['index']
        self.mic_combo.bind("<<ComboboxSelected>>", on_mic_select)

        mic_frame = ttk.Frame(self.main_frame)
        mic_frame.pack(expand=True)

        self.mic_button = tk.Button(mic_frame, text="🎤", font=("Arial", 24),
                                   width=8, height=8,
                                   command=self.toggle_recording,
                                   bg="gray", fg="white",
                                   relief="raised", bd=3)
        self.mic_button.pack()

        self.status_label = ttk.Label(self.main_frame, text=get_text("start_speaking", self.parent.current_language))
        self.status_label.pack(pady=(10, 0))

        self.window.protocol("WM_DELETE_WINDOW", self.hide_window)

        
    def show_window(self):
        if self.window is None:
            self.create_window()
        else:
            # Only update window title to match current app language, but keep STT language choice
            self.window.title(get_text("speech_window_title", self.parent.current_language))
        
        self.window.deiconify()
        if not self.is_recording:
            self.start_recording()
        
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        if self.is_recording:
            return
        try:
            import threading
            import listener
            self.is_recording = True
            self.mic_button.config(bg="#f44336", text="⏹️")
            self.status_label.config(text=get_text("listening", self.parent.current_language))
            self.lang_choice_btn.config(state="disabled")
            self.mic_combo.config(state="disabled")
            language_code = self.language_selector.language
            device_index = self.selected_mic_index
            self._stt_stop_event = threading.Event()
            def run_stt():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                def on_error(err):
                    print("STT Error Callback:", err)
                    self.parent.root.after(0, self.stop_recording)
                    import tkinter.messagebox as messagebox
                    self.parent.root.after(0, lambda: messagebox.showerror(
                        get_text("stt_error", self.parent.current_language), 
                        get_text("stt_error_message", self.parent.current_language)
                    ))
                task = loop.create_task(listener.start_transcribing(language_code=language_code, device_index=device_index, stop_event=self._stt_stop_event, api_key=self.api_key, on_error=on_error))
                try:
                    loop.run_until_complete(task)
                except Exception as e:
                    print(f"STT error: {e}")
                finally:
                    loop.close()
            
            self.save_api_btn.config(state="disabled")
            self._stt_thread = threading.Thread(target=run_stt, daemon=True)
            self._stt_thread.start()
        except Exception as e:
            self.is_recording = False
            self.mic_button.config(bg="#4CAF50", text="🎤")
            self.status_label.config(text=get_text("error_occurred", self.parent.current_language))
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                get_text("error", self.parent.current_language), 
                get_text("recording_error", self.parent.current_language).format(str(e))
            )

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.mic_button.config(bg="#4CAF50", text="🎤")
        self.status_label.config(text=get_text("start_speaking", self.parent.current_language))
        self.lang_choice_btn.config(state="normal")
        self.mic_combo.config(state="readonly")
        self.save_api_btn.config(state="normal")
        try:
            if hasattr(self, '_stt_stop_event') and self._stt_stop_event is not None:
                self._stt_stop_event.set()
            if hasattr(self, '_stt_thread') and self._stt_thread.is_alive():
                self._stt_thread.join(timeout=3)
        except Exception as e:
            print(f"STT thread stopping error: {e}")

    def hide_window(self):
        if self.is_recording:
            self.stop_recording()
        if self.window:
            self.window.withdraw()