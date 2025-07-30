import keyboard
import pygame
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import math
import time
import json
import mouse
import os

from speech_ui import SpeechToTextWindow
from translations import get_text, get_available_languages, get_language_names


class PS4ControllerApp:
    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            return {"language": "en", "SPEECHMATICS_API_KEY": ""}
    
    def load_api_key(self):
        settings = self.load_settings()
        return settings.get("SPEECHMATICS_API_KEY", "")
    
    def load_language(self):
        settings = self.load_settings()
        return settings.get("language", "en")

    def save_settings(self, settings):
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise e
    
    def save_api_key(self):
        new_key = self.api_key_var.get().strip()

        try:
            settings = self.load_settings()
            settings["SPEECHMATICS_API_KEY"] = new_key
            self.save_settings(settings)
            self.api_key = new_key
            self.speech_window.update_api_key(new_key)
            self.update_api_key_status()
            if new_key == "":
                messagebox.showinfo(get_text("success", self.current_language), get_text("api_clear_success", self.current_language))
            else:
                messagebox.showinfo(get_text("success", self.current_language), get_text("api_save_success", self.current_language))
        except Exception as e:
            messagebox.showerror(get_text("error", self.current_language), get_text("api_save_error", self.current_language).format(e))
    
    def apply_language(self):
        try:
            # Get selected language from combobox
            selected = self.language_combo.get()
            if " - " in selected:
                new_language = selected.split(" - ")[0]
            else:
                new_language = selected
            
            if new_language != self.current_language:
                # Save new language to settings
                settings = self.load_settings()
                settings["language"] = new_language
                self.save_settings(settings)
                
                # Show success message and ask for restart
                messagebox.showinfo(
                    get_text("success", new_language), 
                    get_text("language_applied", new_language)
                )
        except Exception as e:
            messagebox.showerror(get_text("error", self.current_language), get_text("language_apply_error", self.current_language))

    def copy_api_key(self, event=None):
        if self.api_key_entry.selection_present():
            try:
                start = self.api_key_entry.index("sel.first")
                end = self.api_key_entry.index("sel.last")
                selected_text = self.api_key_var.get()[start:end]
                
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                return "break" # Prevent default copy action
            except tk.TclError:
                # This can happen if the selection is lost, just ignore it.
                pass

    def __init__(self):
        # Load settings first
        self.current_language = self.load_language()
        
        self.root = tk.Tk()
        self.root.title(get_text("app_title", self.current_language))
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        self.controller = None
        self.running = False
        self.thread = None
        
        self.api_key = self.load_api_key()
        
        self.keyboard_open = False
        
        self.mouse_sensitivity = 2.0
        self.scroll_sensitivity = 2.0
        
        self.setup_ui()

        self.speech_window = SpeechToTextWindow(self, self.api_key, self.save_api_btn)

        self.init_pygame()
        self.update_api_key_status()

    def update_api_key_status(self):
        if self.api_key:
            api_status = get_text("api_status_good", self.current_language)
            api_color = "green"
            self.api_key_status.config(text=f"Speechmatics API: {api_status}", foreground=api_color)
            
            if hasattr(self, 'speech_window'):
                self.speech_window.api_key = self.api_key
        else:
            api_status = get_text("api_status_bad", self.current_language)
            api_color = "red"
            self.api_key_status.config(text=f"Speechmatics API: {api_status}", foreground=api_color)
        
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.main_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.main_frame, text=get_text("main_tab", self.current_language))

        title_label = ttk.Label(self.main_frame, text=get_text("app_title", self.current_language), 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))

        self.settings_frame = ttk.Frame(self.notebook, padding="16")
        self.notebook.add(self.settings_frame, text=get_text("api_settings_tab", self.current_language))
        ttk.Label(self.settings_frame, text=get_text("api_key_label", self.current_language), font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0,8))
        self.api_key_var = tk.StringVar(value=self.load_api_key() or "")
        self.api_key_entry = ttk.Entry(self.settings_frame, textvariable=self.api_key_var, width=40, show='*')
        self.api_key_entry.grid(row=1, column=0, sticky=tk.W, padx=(0,10))
        self.api_key_entry.bind("<<Copy>>", self.copy_api_key)

        self.api_key_show = False
        def toggle_api_key_visibility():
            self.api_key_show = not self.api_key_show
            self.api_key_entry.config(show='' if self.api_key_show else '*')
            self.api_key_eye_btn.config(text='👁️' if not self.api_key_show else '🚫')
        self.api_key_eye_btn = ttk.Button(self.settings_frame, text='👁️', width=3, command=toggle_api_key_visibility)
        self.api_key_eye_btn.grid(row=1, column=2, padx=(4,0))

        self.save_api_btn = ttk.Button(self.settings_frame, text=get_text("save_api_key", self.current_language), command=self.save_api_key)
        self.save_api_btn.grid(row=1, column=3, padx=(10,0))
        
        # Language Settings Tab
        self.language_frame = ttk.Frame(self.notebook, padding="16")
        self.notebook.add(self.language_frame, text=get_text("language_settings_tab", self.current_language))
        
        ttk.Label(self.language_frame, text=get_text("language_selection", self.current_language), font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0,8))
        
        current_lang_frame = ttk.Frame(self.language_frame)
        current_lang_frame.grid(row=1, column=0, sticky=tk.W, pady=(0,10))
        
        ttk.Label(current_lang_frame, text=get_text("current_language", self.current_language)).grid(row=0, column=0, sticky=tk.W)
        
        language_names = get_language_names()
        current_lang_name = language_names.get(self.current_language, self.current_language)
        self.current_lang_label = ttk.Label(current_lang_frame, text=current_lang_name, font=("Arial", 10, "bold"))
        self.current_lang_label.grid(row=0, column=1, padx=(10,0))
        
        select_lang_frame = ttk.Frame(self.language_frame)
        select_lang_frame.grid(row=2, column=0, sticky=tk.W, pady=(0,10))
        
        ttk.Label(select_lang_frame, text=get_text("select_language", self.current_language)).grid(row=0, column=0, sticky=tk.W)
        
        self.language_var = tk.StringVar(value=self.current_language)
        self.language_combo = ttk.Combobox(select_lang_frame, textvariable=self.language_var, 
                                          values=list(language_names.keys()), state="readonly", width=15)
        self.language_combo.grid(row=0, column=1, padx=(10,0))
        
        # Set display names in combobox
        self.language_combo['values'] = [f"{code} - {name}" for code, name in language_names.items()]
        current_display = f"{self.current_language} - {current_lang_name}"
        self.language_combo.set(current_display)
        
        self.apply_lang_btn = ttk.Button(self.language_frame, text=get_text("apply_language", self.current_language), 
                                        command=self.apply_language)
        self.apply_lang_btn.grid(row=3, column=0, sticky=tk.W, pady=(10,0))

        status_frame = ttk.LabelFrame(self.main_frame, text=get_text("controller_status", self.current_language), padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text=get_text("controller_not_connected", self.current_language), 
                                     foreground="red")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.refresh_btn = ttk.Button(status_frame, text=get_text("refresh_controller", self.current_language), 
                                     command=self.refresh_controller)
        self.refresh_btn.grid(row=0, column=1, padx=(10, 0))
        
        speech_frame = ttk.LabelFrame(self.main_frame, text="Speech-to-Text Durumu", padding="10")
        speech_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.api_key_status = ttk.Label(speech_frame)
        self.api_key_status.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.start_btn = ttk.Button(control_frame, text=get_text("start_control", self.current_language), 
                                   command=self.start_control, state="disabled")
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text=get_text("stop_control", self.current_language), 
                                  command=self.stop_control, state="disabled")
        self.stop_btn.grid(row=0, column=1)
        
        test_frame = ttk.Frame(self.main_frame)
        test_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))

        sensitivity_frame = ttk.LabelFrame(self.main_frame, text="Sensitivity Settings", padding="10")
        sensitivity_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(sensitivity_frame, text=get_text("mouse_sensitivity", self.current_language)).grid(row=0, column=0, sticky=tk.W)
        self.mouse_sens_scale = ttk.Scale(sensitivity_frame, from_=40, to=100, 
                                         orient=tk.HORIZONTAL, length=200,
                                         command=self.update_mouse_sensitivity)
        self.mouse_sens_scale.set(50)
        self.mouse_sens_scale.grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(sensitivity_frame, text=get_text("scroll_sensitivity", self.current_language)).grid(row=1, column=0, sticky=tk.W)
        self.scroll_sens_scale = ttk.Scale(sensitivity_frame, from_=20, to=60, 
                                          orient=tk.HORIZONTAL, length=200,
                                          command=self.update_scroll_sensitivity)
        self.scroll_sens_scale.set(50)
        self.scroll_sens_scale.grid(row=1, column=1, padx=(10, 0))
        
        controls_frame = ttk.LabelFrame(self.main_frame, text=get_text("controls_title", self.current_language), padding="10")
        controls_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        tree_frame = ttk.Frame(controls_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.controls_tree = ttk.Treeview(tree_frame, columns=("Function",), show="tree headings", height=10)
        self.controls_tree.heading("#0", text="Controller" if self.current_language == "en" else "Controller Tuşu")
        self.controls_tree.heading("Function", text="Function" if self.current_language == "en" else "Fonksiyon")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.controls_tree.yview)
        self.controls_tree.configure(yscrollcommand=scrollbar.set)
        
        self.controls_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.populate_controls_tree()
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(6, weight=1)
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
    def populate_controls_tree(self):
        if self.current_language == "en":
            controls_mapping = [
                ("Left Stick", get_text("left_stick", self.current_language)),
                ("Right Stick", get_text("right_stick", self.current_language)),
                ("X / L3", get_text("x_button", self.current_language)),
                ("R3", get_text("r3_button", self.current_language)),
                ("Square", get_text("square_button", self.current_language)),
                ("Triangle", get_text("triangle_button", self.current_language)),
                ("Circle", get_text("circle_button", self.current_language)),
                ("D-Pad", get_text("dpad", self.current_language)),
                ("PS4 Button", get_text("ps4_button", self.current_language)),
                ("Touchpad", get_text("touchpad", self.current_language)),
                ("Options", get_text("options_button", self.current_language)),
                ("L1/L2", get_text("l1_l2", self.current_language)),
                ("R1/R2", get_text("r1_r2", self.current_language))
            ]
        else:
            controls_mapping = [
                ("Sol Analog", get_text("left_stick", self.current_language)),
                ("Sağ Analog", get_text("right_stick", self.current_language)),
                ("X / L3", get_text("x_button", self.current_language)),
                ("R3", get_text("r3_button", self.current_language)),
                ("Kare", get_text("square_button", self.current_language)),
                ("Üçgen", get_text("triangle_button", self.current_language)),
                ("Daire", get_text("circle_button", self.current_language)),
                ("D-pad", get_text("dpad", self.current_language)),
                ("PS4 Tuşu", get_text("ps4_button", self.current_language)),
                ("Touchpad", get_text("touchpad", self.current_language)),
                ("Options", get_text("options_button", self.current_language)),
                ("L1/L2", get_text("l1_l2", self.current_language)),
                ("R1/R2", get_text("r1_r2", self.current_language))
            ]
        
        self.controls_tree.delete(*self.controls_tree.get_children())
        
        for controller_key, function in controls_mapping:
            self.controls_tree.insert("", "end", text=controller_key, values=(function,))
    
    def init_pygame(self):
        try:
            pygame.init()
            pygame.joystick.init()
        except Exception as e:
            messagebox.showerror("Hata", f"Pygame başlatılamadı: {str(e)}")
    
    def refresh_controller(self):
        try:
            if pygame.joystick.get_count() > 0:
                self.controller = pygame.joystick.Joystick(0)
                self.controller.init()
                self.status_label.config(text=f"✅ {self.controller.get_name()}", foreground="green")
                self.start_btn.config(state="normal")
                self.start_control()
            else:
                self.controller = None
                self.status_label.config(text=get_text("controller_not_connected", self.current_language), foreground="red")
                self.start_btn.config(state="disabled")
                self.stop_control()
        except Exception as e:
            self.controller = None
            self.status_label.config(text=f"❌ {get_text('error', self.current_language)}: {str(e)}", foreground="red")
            self.start_btn.config(state="disabled")
            messagebox.showerror("Hata", f"Controller kontrol edilemedi: {str(e)}")
    
    def update_mouse_sensitivity(self, value):
        self.mouse_sensitivity = float(value) * 0.04
    
    def update_scroll_sensitivity(self, value):
        self.scroll_sensitivity = float(value) * 0.02
    
    def start_control(self):
        if self.running:
            return None

        if not self.controller:
            messagebox.showwarning("Uyarı", "Controller bağlı değil!")
            return
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        self.thread = threading.Thread(target=self.control_loop, daemon=True)
        self.thread.start()
    
    def stop_control(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
    
    def toggle_onscreen_keyboard(self):
        try:
            pyautogui.hotkey('win', 'ctrl', 'o')
            self.keyboard_open = not self.keyboard_open
        except Exception as e:
            print(f"Couldn't open onscreen keyboard: {e}")
    
    def control_loop(self):
        clock = pygame.time.Clock()
        
        while self.running:
            if pygame.joystick.get_count() == 0:
                self.refresh_controller()
                break

            pygame.event.pump()
            
            if not self.controller:
                break
            
            events = pygame.event.get()
            names = ["x", "circle", "square", "triangle", "share", "ps4", "options", "l3", "r3", "l1", "r1", "pad-up", "pad-down", "pad-left", "pad-right", "touchpad"]
            
            def get(name):
                return names[event.button] == name
        
            if not hasattr(self, '_r1_last_press_time'):
                self._r1_last_press_time = 0
            if not hasattr(self, '_r1_click_count'):
                self._r1_click_count = 0
            if not hasattr(self, '_r1_is_holding'):
                self._r1_is_holding = False
            if not hasattr(self, '_r1_timer_start'):
                self._r1_timer_start = 0
            if not hasattr(self, '_l1_last_press_time'):
                self._l1_last_press_time = 0

            DOUBLE_CLICK_THRESHOLD = 0.35
            HOLD_THRESHOLD = 0.4
            import threading

            for event in events:
                now = time.time()
                if event.type == pygame.JOYBUTTONDOWN and get("r1"):
                    self._r1_timer_start = now
                    self._r1_is_holding = True
                    if now - self._r1_last_press_time < DOUBLE_CLICK_THRESHOLD:
                        self._r1_click_count += 1
                    else:
                        self._r1_click_count = 1
                    self._r1_last_press_time = now
                    continue
                elif event.type == pygame.JOYBUTTONUP and get("r1"):
                    hold_time = now - self._r1_timer_start
                    self._r1_is_holding = False
                    if hold_time > HOLD_THRESHOLD:
                        keyboard.release('shift')
                    else:
                        if self._r1_click_count == 2:
                            pyautogui.hotkey('ctrl', 'x')
                            self._r1_click_count = 0
                        elif self._r1_click_count == 1:
                            def delayed_copy():
                                time.sleep(DOUBLE_CLICK_THRESHOLD)
                                if self._r1_click_count == 1:
                                    pyautogui.hotkey('ctrl', 'c')
                                    self._r1_click_count = 0
                            threading.Thread(target=delayed_copy, daemon=True).start()
                    continue
                if self._r1_is_holding and (time.time() - self._r1_timer_start) > HOLD_THRESHOLD:
                    if not keyboard.is_pressed('shift'):
                        keyboard.press('shift')
                if event.type == pygame.JOYBUTTONDOWN and get("l1"):
                    pyautogui.hotkey('ctrl', 'v')
                    continue

                if event.type == pygame.JOYBUTTONDOWN and get("share"):
                    pyautogui.press('enter')
                    continue
                if not hasattr(self, '_l2_pressed'):
                    self._l2_pressed = False
                L2_AXIS = 4
                L2_THRESHOLD = 0.5
                if event.type == pygame.JOYAXISMOTION and event.axis == L2_AXIS:
                    if event.value > L2_THRESHOLD and not self._l2_pressed:
                        self._l2_pressed = True
                        keyboard.press('alt')
                    elif event.value < L2_THRESHOLD and self._l2_pressed:
                        self._l2_pressed = False
                        keyboard.release('alt')

                if not hasattr(self, '_r2_last_press_time'):
                    self._r2_last_press_time = 0
                if not hasattr(self, '_r2_click_count'):
                    self._r2_click_count = 0
                if not hasattr(self, '_r2_last_value'):
                    self._r2_last_value = 0.0
                if not hasattr(self, '_r2_pressed'):
                    self._r2_pressed = False
                R2_AXIS = 5
                R2_THRESHOLD = 0.7
                if event.type == pygame.JOYAXISMOTION and event.axis == R2_AXIS:
                    if event.value > R2_THRESHOLD and not self._r2_pressed:
                        self._r2_pressed = True
                        now = time.time()
                        if now - self._r2_last_press_time < 0.35:
                            self._r2_click_count += 1
                        else:
                            self._r2_click_count = 1
                        self._r2_last_press_time = now
                    elif event.value < R2_THRESHOLD and self._r2_pressed:
                        self._r2_pressed = False
                        if self._r2_click_count == 2:
                            pyautogui.hotkey('ctrl', 'shift', 'z')
                            self._r2_click_count = 0
                        elif self._r2_click_count == 1:
                            def delayed_undo():
                                time.sleep(0.35)
                                if self._r2_click_count == 1:
                                    pyautogui.hotkey('ctrl', 'z')
                                    self._r2_click_count = 0
                            threading.Thread(target=delayed_undo, daemon=True).start()
                    self._r2_last_value = event.value
                    continue
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if get("x") or get("l3"):
                        pyautogui.mouseDown()
                    
                    elif get("r3"):
                        pyautogui.click(button='right')
                    
                    elif get("circle"):
                        pyautogui.press('esc')
                    
                    elif get("ps4"):
                        pyautogui.press('win')
                    
                    elif get("touchpad"):
                        self.toggle_onscreen_keyboard()
                    
                    elif get("options"):
                        if self.speech_window.window and self.speech_window.window.state() == 'normal':
                            if self.speech_window.is_recording:
                                self.speech_window.stop_recording()
                            self.speech_window.hide_window()
                        else:
                            self.speech_window.show_window()
                        continue
                    
                elif event.type == pygame.JOYBUTTONUP:
                    if get("x") or get("l3"):
                        pyautogui.mouseUp()

            def get(name):
                return self.controller.get_button(names.index(name))
            
            if get("pad-left"):
                pyautogui.press('left')

            if get("pad-right"):
                if self._l2_pressed:
                    pyautogui.press('tab')
                    time.sleep(0.1)
                else:
                    pyautogui.press('right')
            
            if get("pad-up"):
                pyautogui.press('up')

            if get("pad-down"):
                pyautogui.press('down')

            if get("triangle"):
                pyautogui.press('space')
            
            if get("square"):
                pyautogui.press('backspace')

            DEADZONE = 0.1

            def apply_deadzone(value):
                return 0 if abs(value) < DEADZONE else value

            lx = apply_deadzone(self.controller.get_axis(0))
            ly = apply_deadzone(self.controller.get_axis(1))

            (X,Y)=mouse.get_position()
            if lx != 0 or ly != 0:
                alive_process = True
                mouse.move(X+ lx * self.mouse_sensitivity, Y + ly * self.mouse_sensitivity)
                time.sleep(0.001 / math.sqrt(math.pow(lx,2) + math.pow(ly,2)))

            rx = apply_deadzone(self.controller.get_axis(2))
            ry = apply_deadzone(self.controller.get_axis(3))

            if abs(ry) > 0:
                alive_process = True
                mouse.wheel(delta=round(-ry) * self.scroll_sensitivity)
                time.sleep(0.05)

            DEADZONE_H_SCROLL = 0.35
            if abs(rx) > DEADZONE_H_SCROLL:
                pyautogui.hscroll(int(rx * 100))
                if abs(ry) == 0:
                    time.sleep(0.015)
            
            clock.tick(720)  # FPS
    
        
        self.running = False
        self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
        self.root.after(0, lambda: self.start_btn.config(state="normal"))
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.refresh_controller()
        self.root.mainloop()
    
    def on_closing(self):
        self.stop_control()
        if self.speech_window.is_recording:
            self.speech_window.stop_recording()
        if self.speech_window.window:
            self.speech_window.hide_window()
        if self.keyboard_open:
            self.toggle_onscreen_keyboard()
        self.root.destroy()

def main():
    try:
        app = PS4ControllerApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    main()
