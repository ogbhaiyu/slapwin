"""SlapWin — Windows Charger Novelty Tool (Main GUI Application)"""

__version__ = "1.0.0"

import os
import sys
import json
import winreg
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

# Import backend helpers
import charger_monitor


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class SlapWinApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title(f"SlapWin v{__version__}")
        self.geometry("700x550")
        self.resizable(False, False)

        # Set Window Icon
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Apply premium dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Default styling configuration
        self.configure(fg_color="#0b0813")

        # Load logo image for CustomTkinter
        logo_png_path = resource_path("logo.png")
        self.logo_image = None
        if os.path.exists(logo_png_path):
            try:
                pil_img = Image.open(logo_png_path)
                self.logo_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(30, 30))
            except Exception:
                pass

        # Load current settings
        self.settings = charger_monitor.load_settings()

        # Main Layout: Sidebar & Content Area
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0, fg_color="#0d0a1b")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        if self.logo_image:
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame,
                text=" SlapWin",
                image=self.logo_image,
                compound="left",
                font=("Outfit", 22, "bold"),
                text_color="#ff2a74"
            )
        else:
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame,
                text="⚡ SlapWin",
                font=("Outfit", 22, "bold"),
                text_color="#ff2a74"
            )
        self.logo_label.grid(row=0, column=0, padx=20, pady=25)

        self.dashboard_btn = ctk.CTkButton(self.sidebar_frame, text="Dashboard", font=("Space Grotesk", 14), fg_color="transparent", text_color="#f5f2fd", hover_color="#1a1435", anchor="w", command=self.show_dashboard)
        self.dashboard_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.customize_btn = ctk.CTkButton(self.sidebar_frame, text="Customize Sound", font=("Space Grotesk", 14), fg_color="transparent", text_color="#f5f2fd", hover_color="#1a1435", anchor="w", command=self.show_customize)
        self.customize_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        self.prank_btn = ctk.CTkButton(self.sidebar_frame, text="Prank Builder 😈", font=("Space Grotesk", 14), fg_color="transparent", text_color="#f5f2fd", hover_color="#1a1435", anchor="w", command=self.show_prank)
        self.prank_btn.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        self.version_badge = ctk.CTkLabel(self.sidebar_frame, text=f"SlapWin v{__version__}", font=("Space Grotesk", 10), text_color="#9f96b9")
        self.version_badge.grid(row=5, column=0, pady=20)

        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Initialize views
        self.init_dashboard_view()
        self.init_customize_view()
        self.init_prank_view()

        # Show Dashboard initially
        self.show_dashboard()

        # Start background polling/monitor
        self.start_monitoring_service()

    def start_monitoring_service(self):
        self.monitor_thread = threading.Thread(target=charger_monitor.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def show_dashboard(self):
        self.customize_frame.grid_forget()
        self.prank_frame.grid_forget()
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.dashboard_btn.configure(fg_color="#1a1435", text_color="#ff2a74")
        self.customize_btn.configure(fg_color="transparent", text_color="#f5f2fd")
        self.prank_btn.configure(fg_color="transparent", text_color="#f5f2fd")

    def show_customize(self):
        self.dashboard_frame.grid_forget()
        self.prank_frame.grid_forget()
        self.customize_frame.grid(row=0, column=0, sticky="nsew")
        self.customize_btn.configure(fg_color="#1a1435", text_color="#ff2a74")
        self.dashboard_btn.configure(fg_color="transparent", text_color="#f5f2fd")
        self.prank_btn.configure(fg_color="transparent", text_color="#f5f2fd")

    def show_prank(self):
        self.dashboard_frame.grid_forget()
        self.customize_frame.grid_forget()
        self.prank_frame.grid(row=0, column=0, sticky="nsew")
        self.prank_btn.configure(fg_color="#1a1435", text_color="#ff2a74")
        self.dashboard_btn.configure(fg_color="transparent", text_color="#f5f2fd")
        self.customize_btn.configure(fg_color="transparent", text_color="#f5f2fd")

    # ==================== VIEW INITIALIZATIONS ====================

    def init_dashboard_view(self):
        self.dashboard_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Header
        lbl = ctk.CTkLabel(self.dashboard_frame, text="Dashboard", font=("Outfit", 26, "bold"), text_color="#f5f2fd")
        lbl.pack(anchor="w", pady=(0, 20))

        # Status Card
        self.status_card = ctk.CTkFrame(self.dashboard_frame, fg_color="#161027", border_color="#8a2be2", border_width=1, corner_radius=16)
        self.status_card.pack(fill="x", pady=10)

        self.status_lbl = ctk.CTkLabel(self.status_card, text="ACTIVE", font=("Outfit", 18, "bold"), text_color="#00ffaa")
        self.status_lbl.pack(side="left", padx=20, pady=25)

        # Toggle
        self.active_switch = ctk.CTkSwitch(
            self.status_card,
            text="Enable Charger Sound",
            font=("Space Grotesk", 14),
            progress_color="#ff2a74",
            command=self.toggle_active
        )
        self.active_switch.pack(side="right", padx=20)
        if self.settings.get("active", True):
            self.active_switch.select()
            self.status_lbl.configure(text="ACTIVE", text_color="#00ffaa")
        else:
            self.active_switch.deselect()
            self.status_lbl.configure(text="PAUSED", text_color="#ff2a74")

        # Test Section
        self.test_card = ctk.CTkFrame(self.dashboard_frame, fg_color="#161027", corner_radius=16)
        self.test_card.pack(fill="x", pady=15)

        test_title = ctk.CTkLabel(self.test_card, text="Test Playback", font=("Outfit", 16, "bold"), text_color="#f5f2fd")
        test_title.pack(anchor="w", padx=20, pady=(15, 5))

        test_desc = ctk.CTkLabel(self.test_card, text="Trigger the sound effect immediately to check the current output volume.", font=("Space Grotesk", 12), text_color="#9f96b9")
        test_desc.pack(anchor="w", padx=20, pady=(0, 15))

        self.test_btn = ctk.CTkButton(
            self.test_card,
            text="Play Sound",
            font=("Outfit", 14, "bold"),
            fg_color="#ff2a74",
            hover_color="#d61b58",
            corner_radius=8,
            command=self.trigger_test_sound
        )
        self.test_btn.pack(anchor="w", padx=20, pady=(0, 20))

        # Startup options
        self.startup_card = ctk.CTkFrame(self.dashboard_frame, fg_color="#161027", corner_radius=16)
        self.startup_card.pack(fill="x", pady=10)

        self.startup_switch = ctk.CTkSwitch(
            self.startup_card,
            text="Run on Windows Startup",
            font=("Space Grotesk", 14),
            progress_color="#8a2be2",
            command=self.toggle_startup
        )
        self.startup_switch.pack(padx=20, pady=20, anchor="w")
        if self.is_app_in_startup():
            self.startup_switch.select()

    def init_customize_view(self):
        self.customize_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Header
        lbl = ctk.CTkLabel(self.customize_frame, text="Customize Sound Effect", font=("Outfit", 26, "bold"), text_color="#f5f2fd")
        lbl.pack(anchor="w", pady=(0, 20))

        # Current sound card
        current_card = ctk.CTkFrame(self.customize_frame, fg_color="#161027", corner_radius=16)
        current_card.pack(fill="x", pady=(0, 15))

        current_title = ctk.CTkLabel(current_card, text="Current Sound", font=("Outfit", 16, "bold"), text_color="#f5f2fd")
        current_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.current_sound_lbl = ctk.CTkLabel(current_card, text="", font=("Space Grotesk", 11), text_color="#9f96b9", wraplength=420, justify="left")
        self.current_sound_lbl.pack(anchor="w", padx=20, pady=(0, 15))
        self._update_current_sound_label()

        # Custom file picker
        self.file_lbl = ctk.CTkLabel(self.customize_frame, text="Select Custom MP3/WAV file:", font=("Space Grotesk", 14), text_color="#f5f2fd")
        self.file_lbl.pack(anchor="w", pady=(10, 5))

        file_select_row = ctk.CTkFrame(self.customize_frame, fg_color="transparent")
        file_select_row.pack(fill="x", pady=5)

        self.path_entry = ctk.CTkEntry(file_select_row, font=("Space Grotesk", 12), text_color="#f5f2fd", fg_color="#161027", border_color="#8a2be2")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.path_entry.insert(0, self.settings.get("custom_sound_path", ""))

        self.browse_btn = ctk.CTkButton(
            file_select_row,
            text="Browse",
            font=("Space Grotesk", 12, "bold"),
            fg_color="#8a2be2",
            hover_color="#6e20b8",
            width=80,
            command=self.browse_sound_file
        )
        self.browse_btn.pack(side="right")

        # Action buttons row
        btn_row = ctk.CTkFrame(self.customize_frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=(25, 0))
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        # Save Button
        self.save_btn = ctk.CTkButton(
            btn_row,
            text="Save Settings",
            font=("Outfit", 14, "bold"),
            fg_color="#ff2a74",
            hover_color="#d61b58",
            corner_radius=8,
            height=40,
            command=self.save_custom_settings
        )
        self.save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Reset to Default Button
        self.reset_btn = ctk.CTkButton(
            btn_row,
            text="Reset to Default Sound",
            font=("Outfit", 14, "bold"),
            fg_color="#161027",
            hover_color="#1a1435",
            border_color="#8a2be2",
            border_width=1,
            corner_radius=8,
            height=40,
            command=self.reset_to_default_sound
        )
        self.reset_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    def init_prank_view(self):
        self.prank_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Prank upsell card
        prank_card = ctk.CTkFrame(self.prank_frame, fg_color="#161027", border_color="#ff2a74", border_width=1, corner_radius=16)
        prank_card.pack(fill="both", expand=True)

        # Emoji header
        prank_emoji = ctk.CTkLabel(prank_card, text="😈", font=("Outfit", 64))
        prank_emoji.pack(pady=(30, 5))

        # Title
        prank_title = ctk.CTkLabel(prank_card, text="Prank Edition", font=("Outfit", 24, "bold"), text_color="#ff2a74")
        prank_title.pack(pady=(0, 10))

        # Description
        prank_desc = ctk.CTkLabel(
            prank_card,
            text="Get the standalone prank executable that runs invisibly\non your friend's PC and triggers at full volume!",
            font=("Space Grotesk", 13),
            text_color="#f5f2fd",
            justify="center"
        )
        prank_desc.pack(pady=(0, 20))

        # Feature bullets
        features = [
            "Runs 100% invisible in the background",
            "Force system volume to maximum",
            "Plays sound on charger plug-in",
            "Full-screen 'PRANKED!' overlay",
            "One-click deactivate & uninstall",
            "No setup required — just double-click"
        ]
        for feat in features:
            feat_lbl = ctk.CTkLabel(
                prank_card,
                text=f"  {feat}",
                font=("Space Grotesk", 12),
                text_color="#9f96b9",
                anchor="w"
            )
            feat_lbl.pack(anchor="w", padx=40, pady=2)

        # Buy button
        self.prank_buy_btn = ctk.CTkButton(
            prank_card,
            text="Get Prank Edition — $9.99",
            font=("Outfit", 16, "bold"),
            fg_color="#ff2a74",
            hover_color="#d61b58",
            corner_radius=50,
            height=50,
            width=280,
            command=self.open_prank_gumroad
        )
        self.prank_buy_btn.pack(pady=(25, 30))

    # ==================== EVENT HANDLERS ====================

    def toggle_active(self):
        active = self.active_switch.get()
        self.settings["active"] = bool(active)
        charger_monitor.save_settings(self.settings)
        if active:
            self.status_lbl.configure(text="ACTIVE", text_color="#00ffaa")
        else:
            self.status_lbl.configure(text="PAUSED", text_color="#ff2a74")

    def toggle_startup(self):
        val = self.startup_switch.get()
        if val:
            self.add_app_to_startup()
        else:
            self.remove_app_from_startup()

    def change_mode(self, mode):
        pass

    def browse_sound_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Charger Sound File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.aac")]
        )
        if file_path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file_path)

    def save_custom_settings(self):
        path = self.path_entry.get()
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Selected sound file does not exist:\n{path}")
            return
        self.settings["sound_mode"] = "custom"
        self.settings["custom_sound_path"] = path
        charger_monitor.save_settings(self.settings)
        self._update_current_sound_label()
        messagebox.showinfo("Saved", "Settings updated successfully!")

    def trigger_test_sound(self):
        mock_settings = {
            "sound_mode": "custom",
            "custom_sound_path": self.path_entry.get(),
            "max_volume_on_trigger": False
        }
        charger_monitor.trigger_alert(mock_settings)

    def reset_to_default_sound(self):
        default_path = resource_path("daddy.mp3")
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, default_path)
        self.settings["sound_mode"] = "custom"
        self.settings["custom_sound_path"] = default_path
        charger_monitor.save_settings(self.settings)
        self._update_current_sound_label()
        messagebox.showinfo("Reset", "Sound reset to the default effect!")

    def _update_current_sound_label(self):
        path = self.settings.get("custom_sound_path", "")
        default_path = resource_path("daddy.mp3")
        if path == default_path or os.path.basename(path) == "daddy.mp3":
            self.current_sound_lbl.configure(text="Default sound effect (daddy.mp3)", text_color="#00ffaa")
        elif path:
            self.current_sound_lbl.configure(text=f"Custom: {os.path.basename(path)}", text_color="#8a2be2")
        else:
            self.current_sound_lbl.configure(text="No sound selected", text_color="#ff2a74")

    def open_prank_gumroad(self):
        import webbrowser
        webbrowser.open("https://YOUR_GUMROAD_LINK.gumroad.com/l/slapwin-prank")

    # ==================== STARTUP REGISTRY METHODS ====================

    def add_app_to_startup(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if sys.argv[0].endswith(".exe"):
                exe_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "SlapWinApp", 0, winreg.REG_SZ, exe_path)
            else:
                py_exe = sys.executable
                script_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, "SlapWinApp", 0, winreg.REG_SZ, f'"{py_exe}" "{script_path}"')
            winreg.CloseKey(key)
        except Exception:
            pass

    def remove_app_from_startup(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "SlapWinApp")
            winreg.CloseKey(key)
        except Exception:
            pass

    def is_app_in_startup(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "SlapWinApp")
            winreg.CloseKey(key)
            return True
        except Exception:
            return False


if __name__ == "__main__":
    app = SlapWinApp()
    app.mainloop()
