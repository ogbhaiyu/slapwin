"""SlapWin Prank Service — Standalone background prank executable."""

__version__ = "1.0.0"

import os
import sys
import time
import ctypes
from ctypes import wintypes
import winreg
import threading

try:
    import win32com.client
except Exception:
    pass

import customtkinter as ctk


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', wintypes.BYTE),
        ('BatteryFlag', wintypes.BYTE),
        ('BatteryLifePercent', wintypes.BYTE),
        ('SystemStatusFlag', wintypes.BYTE),
        ('BatteryLifeTime', wintypes.DWORD),
        ('BatteryFullLifeTime', wintypes.DWORD),
    ]


def get_ac_status():
    status = SYSTEM_POWER_STATUS()
    if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        return status.ACLineStatus
    return 0


def has_battery():
    status = SYSTEM_POWER_STATUS()
    if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        return status.BatteryFlag != 128
    return False


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def set_max_volume():
    for _ in range(50):
        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        time.sleep(0.01)


def play_sound():
    sound_path = resource_path("daddy.mp3")
    if os.path.exists(sound_path):
        try:
            ctypes.windll.winmm.mciSendStringW("close slap_sound", None, 0, None)
            cmd_open = f'open "{sound_path}" type mpegvideo alias slap_sound'
            ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
            ctypes.windll.winmm.mciSendStringW("play slap_sound", None, 0, None)
            return
        except Exception:
            pass

    # Fallback to TTS if audio file fails
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        for voice in speaker.GetVoices():
            if "Zira" in voice.GetDescription():
                speaker.Voice = voice
                break
        speaker.Rate = -3
        speaker.Speak("Yeah... right there... daddy... ohhh")
    except Exception:
        pass


def add_to_startup():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if sys.argv[0].endswith(".exe"):
            exe_path = os.path.abspath(sys.argv[0])
            winreg.SetValueEx(key, "SlapWinPrank", 0, winreg.REG_SZ, f'"{exe_path}" --startup')
        else:
            py_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            winreg.SetValueEx(key, "SlapWinPrank", 0, winreg.REG_SZ, f'"{py_exe}" "{script_path}" --startup')
        winreg.CloseKey(key)
    except Exception:
        pass


def remove_from_startup():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "SlapWinPrank")
        winreg.CloseKey(key)
    except Exception:
        pass


class PrankOverlay(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SlapWin - PRANKED!")
        self.attributes("-topmost", True)
        self.attributes("-fullscreen", True)

        # Set Window Icon
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Color theme
        self.configure(fg_color="#0b0813")

        # Frame
        self.frame = ctk.CTkFrame(self, fg_color="#161027", border_color="#ff2a74", border_width=2, corner_radius=24)
        self.frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.7, relheight=0.6)

        # Header
        self.emoji_label = ctk.CTkLabel(self.frame, text="😜", font=("Outfit", 120))
        self.emoji_label.pack(pady=(40, 10))

        self.title_label = ctk.CTkLabel(
            self.frame,
            text="YOU HAVE BEEN PRANKED!",
            font=("Outfit", 42, "bold"),
            text_color="#ff2a74"
        )
        self.title_label.pack(pady=10)

        self.desc_label = ctk.CTkLabel(
            self.frame,
            text="Your computer was successfully setup with SlapWin.\nNext time, lock your screen when you step away! ⚡",
            font=("Space Grotesk", 18),
            text_color="#f5f2fd",
            justify="center"
        )
        self.desc_label.pack(pady=20)

        # Clean-up Button
        self.exit_btn = ctk.CTkButton(
            self.frame,
            text="Deactivate Prank & Uninstall",
            font=("Outfit", 16, "bold"),
            fg_color="#ff2a74",
            hover_color="#d61b58",
            corner_radius=50,
            height=50,
            width=280,
            command=self.deactivate_and_exit
        )
        self.exit_btn.pack(pady=30)

    def deactivate_and_exit(self):
        remove_from_startup()
        self.destroy()
        sys.exit(0)


prank_mutex = None


def main():
    global prank_mutex
    try:
        # Single-Instance Protection
        ctypes.windll.kernel32.SetLastError(0)
        prank_mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "Local\\SlapWinPrankMutex")
        last_error = ctypes.windll.kernel32.GetLastError()

        is_startup = len(sys.argv) > 1 and sys.argv[1] == "--startup"

        if last_error == 183:  # ERROR_ALREADY_EXISTS
            if is_startup:
                sys.exit(0)
            else:
                msg = (
                    "SlapWin Prank is already running silently in the background.\n\n"
                    "Would you like to test/preview the prank overlay screen right now?"
                )
                res = ctypes.windll.user32.MessageBoxW(0, msg, "SlapWin - Already Running 😈", 4 | 64 | 256 | 0x00040000)
                if res == 6:  # IDYES
                    set_max_volume()
                    play_sound()
                    app = PrankOverlay()
                    app.mainloop()
                sys.exit(0)

        # Test Preview Mode
        if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t"):
            set_max_volume()
            play_sound()
            app = PrankOverlay()
            app.mainloop()
            return

        add_to_startup()

        # Manual launch: show activation dialog
        is_startup = len(sys.argv) > 1 and sys.argv[1] == "--startup"
        if not is_startup:
            has_bat = has_battery()
            if not has_bat:
                msg = (
                    "SlapWin Prank mode has been activated in the background.\n\n"
                    "⚠️ WARNING: This system does not have a battery (Desktop PC or VM). "
                    "The background charger-connection trigger will not work on this machine because "
                    "the power status is always reported as plugged in.\n\n"
                    "Would you like to test the prank overlay screen right now?"
                )
            else:
                msg = (
                    "SlapWin Prank mode has been activated and is now running silently in the background.\n\n"
                    "To trigger the prank, unplug your laptop charger and plug it back in.\n\n"
                    "Would you like to test the prank overlay screen right now?"
                )

            res = ctypes.windll.user32.MessageBoxW(0, msg, "SlapWin - Prank Activated 😈", 4 | 64 | 256 | 0x00040000)
            if res == 6:  # IDYES
                set_max_volume()
                play_sound()
                app = PrankOverlay()
                app.mainloop()
                return
            else:
                if not has_bat:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        "Prank monitoring started.\n\nNote: Since this machine has no battery, the prank will not trigger unless launched with the test option.",
                        "SlapWin",
                        0 | 48 | 0x00040000
                    )
                else:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        "Prank monitoring started in the background.\n\nUnplug your charger and plug it back in to trigger!",
                        "SlapWin",
                        0 | 64 | 0x00040000
                    )

        # Background monitoring loop
        last_state = get_ac_status()
        while True:
            current_state = get_ac_status()
            if current_state == 1 and last_state == 0:
                set_max_volume()
                play_sound()
                app = PrankOverlay()
                app.mainloop()
                break
            last_state = current_state
            time.sleep(1.0)
    except Exception:
        pass


if __name__ == "__main__":
    main()
