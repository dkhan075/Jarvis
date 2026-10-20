import os
import re
import time
import subprocess
import datetime

import pyautogui
import pygetwindow as gw
from PIL import ImageGrab

from speak import speak
from paths import app_dir

# Safety: slam the mouse into any screen corner to abort PyAutoGUI instantly
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

SCREENSHOT_DIR = os.path.join(app_dir(), "screenshots")

# Apps Jarvis can launch by name (Windows commands)
APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "file explorer": "explorer",
    "command prompt": "cmd",
}

# Spoken phrase -> keyboard shortcut
HOTKEYS = {
    "new file": ("ctrl", "n"),
    "new tab": ("ctrl", "t"),
    "new window": ("ctrl", "n"),
    "save file": ("ctrl", "s"),
    "save this": ("ctrl", "s"),
    "select all": ("ctrl", "a"),
    "copy this": ("ctrl", "c"),
    "paste": ("ctrl", "v"),
    "undo": ("ctrl", "z"),
    "redo": ("ctrl", "y"),
    "close tab": ("ctrl", "w"),
    "refresh": ("f5",),
}


def get_active_window_title():
    """Parse active window data: returns the title of the focused window."""
    try:
        window = gw.getActiveWindow()
        if window and window.title:
            return window.title
    except Exception:
        pass
    return None


def take_screenshot():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    name = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = os.path.join(SCREENSHOT_DIR, name)
    # Pillow's ImageGrab avoids the pyscreeze dependency problem on Python 3.13
    ImageGrab.grab().save(path)
    return path


def type_text(text):
    """Type into whatever window is focused."""
    title = (get_active_window_title() or "").lower()

    # If the focus is still on the editor/terminal running Jarvis,
    # give the user time to click the target window first.
    if "visual studio code" in title or "powershell" in title or "terminal" in title or title.strip() == "jarvis":
        speak("Click where you want me to type. Typing in 3 seconds.")
        time.sleep(3)
    else:
        time.sleep(0.5)

    text = text[:1].upper() + text[1:]
    pyautogui.write(text, interval=0.03)


def handle_automation(command):
    """
    Returns a string for Jarvis to speak if an automation command matched,
    or None if not.
    """

    # Active window
    if "active window" in command or "which window" in command or "what window" in command:
        title = get_active_window_title()
        if title:
            return f"The active window is {title}"
        return "I could not read the active window."

    # Open the screenshots folder
    if "screenshot" in command and "folder" in command:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        os.startfile(SCREENSHOT_DIR)
        return "Opening the screenshots folder"

    # Screenshot (only when clearly asked to take one)
    if "screenshot" in command and ("take" in command or "capture" in command or command.strip() in ("screenshot", "a screenshot")):
        try:
            take_screenshot()
            return "Screenshot saved in the screenshots folder"
        except Exception as e:
            print(f"Screenshot error: {e}")
            return "Sorry, I could not take the screenshot."

    # Typing: matches "type hello" and also "I said type hello"
    match = re.search(r"\b(?:type|write)\s+(.+)", command)
    if match and not command.startswith("write a ") and "write code" not in command:
        text = match.group(1).strip()
        if text:
            type_text(text)
            return "Done typing"

    # Create a fresh Notepad file
    if "notepad" in command and ("new" in command or "create" in command):
        subprocess.Popen("notepad", shell=True)
        time.sleep(1.5)
        pyautogui.hotkey("ctrl", "n")
        return "New Notepad file ready"

    # Keyboard shortcuts
    for phrase, keys in HOTKEYS.items():
        if phrase in command:
            pyautogui.hotkey(*keys)
            return "Done"

    # Scrolling
    if "scroll down" in command:
        pyautogui.scroll(-600)
        return "Scrolling down"
    if "scroll up" in command:
        pyautogui.scroll(600)
        return "Scrolling up"

    # Volume
    if "volume up" in command:
        pyautogui.press("volumeup", presses=5)
        return "Volume up"
    if "volume down" in command:
        pyautogui.press("volumedown", presses=5)
        return "Volume down"
    if "mute" in command:
        pyautogui.press("volumemute")
        return "Toggled mute"

    # Window control
    if "show desktop" in command or "minimize all" in command:
        pyautogui.hotkey("win", "d")
        return "Showing desktop"
    if "switch window" in command:
        pyautogui.hotkey("alt", "tab")
        return "Switching window"

    # Open apps
    if "open" in command:
        for name, exe in APPS.items():
            if name in command:
                subprocess.Popen(exe, shell=True)
                return f"Opening {name}"

    return None