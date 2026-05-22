"""SlapWin Charger Monitor — Background power state monitoring and audio playback."""

import os
import sys
import time
import json
import ctypes
import threading
from ctypes import wintypes
import win32com.client


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', wintypes.BYTE),
        ('BatteryFlag', wintypes.BYTE),
        ('BatteryLifePercent', wintypes.BYTE),
        ('SystemStatusFlag', wintypes.BYTE),
        ('BatteryLifeTime', wintypes.DWORD),
        ('BatteryFullLifeTime', wintypes.DWORD),
    ]


SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
DEFAULT_SOUND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daddy.mp3")

DEFAULT_SETTINGS = {
    "active": True,
    "sound_mode": "custom",
    "custom_sound_path": DEFAULT_SOUND,
    "tts_text": "Yeah... right there... daddy... ohhh",
    "tts_rate": -3,
    "max_volume_on_trigger": False
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass


def get_ac_status():
    status = SYSTEM_POWER_STATUS()
    if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        return status.ACLineStatus
    return 0


def play_custom_audio(file_path):
    if not os.path.exists(file_path):
        return
    try:
        ctypes.windll.winmm.mciSendStringW("close slap_sound", None, 0, None)
        cmd_open = f'open "{file_path}" type mpegvideo alias slap_sound'
        ctypes.windll.winmm.mciSendStringW(cmd_open, None, 0, None)
        ctypes.windll.winmm.mciSendStringW("play slap_sound", None, 0, None)
    except Exception:
        pass


def play_tts(text, rate):
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        for voice in speaker.GetVoices():
            if "Zira" in voice.GetDescription():
                speaker.Voice = voice
                break
        speaker.Rate = rate
        speaker.Speak(text)
    except Exception:
        pass


def set_max_volume():
    for _ in range(50):
        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        time.sleep(0.01)


def trigger_alert(settings):
    if settings.get("max_volume_on_trigger", False):
        set_max_volume()

    if settings.get("sound_mode") == "tts":
        text = settings.get("tts_text", "Yeah... right there... daddy... ohhh")
        rate = settings.get("tts_rate", -3)
        threading.Thread(target=play_tts, args=(text, rate), daemon=True).start()
    else:
        sound_path = settings.get("custom_sound_path", DEFAULT_SOUND)
        if not os.path.isabs(sound_path):
            sound_path = os.path.abspath(os.path.join(os.path.dirname(__file__), sound_path))
        threading.Thread(target=play_custom_audio, args=(sound_path,), daemon=True).start()


def monitor_loop():
    last_state = get_ac_status()

    while True:
        settings = load_settings()
        if not settings.get("active", True):
            time.sleep(2)
            continue

        current_state = get_ac_status()

        if current_state == 1 and last_state == 0:
            trigger_alert(settings)

        last_state = current_state
        time.sleep(1.0)


if __name__ == "__main__":
    monitor_loop()
