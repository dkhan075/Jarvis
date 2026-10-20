"""
Tools that Gemini can call.

Gemini reads each function's name, type hints and docstring to decide which
tool fits the user's request and what arguments to pass. So the docstrings
below are not just comments: they are instructions to the AI.
"""
import os
import datetime
import functools
import webbrowser
from urllib.parse import quote_plus

import pyautogui

import extras as ex
import automation as auto
from commands import SITES


def safe(fn):
    """Logs every tool call and turns crashes into text the AI can explain."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"[tool] {fn.__name__} {args or ''}{kwargs or ''}")
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"[tool] {fn.__name__} failed: {e}")
            return f"Error: {e}"
    return wrapper


# ------------------------------------------------------------ information
@safe
def get_current_time_and_date() -> str:
    """Gets the current local time and today's date."""
    return datetime.datetime.now().strftime("%I:%M %p on %A, %d %B %Y")


@safe
def get_weather(city: str) -> str:
    """Gets the current weather for a city.

    Args:
        city: City name, for example "Mumbai".
    """
    return ex.get_weather(city)


@safe
def get_news_headlines() -> str:
    """Gets the latest top news headlines."""
    return ex.news_command()


# --------------------------------------------------------------- web/apps
@safe
def open_website(name: str) -> str:
    """Opens a website in the browser.

    Args:
        name: A site name like "youtube", "gmail", "github", or a domain like "wikipedia.org".
    """
    key = name.lower().strip()
    for site, url in SITES.items():
        if site in key:
            webbrowser.open(url)
            return f"Opened {site}"
    if "." in key:
        webbrowser.open(key if key.startswith("http") else f"https://{key}")
        return f"Opened {key}"
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(key)}")
    return f"I did not know that site, so I searched Google for {key}"


@safe
def search_google(query: str) -> str:
    """Opens a Google search for the given query in the browser.

    Args:
        query: What to search for.
    """
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
    return f"Opened Google search for {query}"


@safe
def play_on_youtube(query: str) -> str:
    """Opens YouTube search results for a song, video or topic.

    Args:
        query: The song, video or topic to play.
    """
    webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    return f"Opened YouTube results for {query}"


@safe
def open_app(app_name: str) -> str:
    """Launches an installed Windows application by name, such as Notepad, Spotify or Word.

    Args:
        app_name: The application's name.
    """
    return ex.open_any_app(f"open {app_name}")


# ----------------------------------------------------- timers, reminders
@safe
def set_timer(seconds: int, message: str) -> str:
    """Sets a timer or reminder that Jarvis will speak aloud when it finishes.

    Args:
        seconds: How long to wait, converted to seconds (5 minutes = 300).
        message: What to remind the user about. Use an empty string for a plain timer.
    """
    if message.strip():
        ex.start_timer(int(seconds), f"Reminder: {message.strip()}")
    else:
        ex.start_timer(int(seconds), "Time is up! Your timer has finished.")
    return f"Timer set for {int(seconds)} seconds"


@safe
def cancel_all_timers() -> str:
    """Cancels every running timer and reminder."""
    return ex.timer_command("cancel timer")


# ------------------------------------------------------------------ notes
@safe
def add_note(text: str) -> str:
    """Saves a note for the user.

    Args:
        text: The note to save.
    """
    return ex.add_note(text)


@safe
def read_notes() -> str:
    """Reads back the user's saved notes."""
    return ex.read_notes()


@safe
def clear_all_notes() -> str:
    """Deletes ALL of the user's saved notes. Only use when the user clearly asks for this."""
    return ex.clear_notes()


# ------------------------------------------------------ desktop control
SHORTCUTS = {
    "new_tab": ("ctrl", "t"),
    "new_file": ("ctrl", "n"),
    "save": ("ctrl", "s"),
    "select_all": ("ctrl", "a"),
    "copy": ("ctrl", "c"),
    "paste": ("ctrl", "v"),
    "undo": ("ctrl", "z"),
    "redo": ("ctrl", "y"),
    "close_tab": ("ctrl", "w"),
    "refresh": ("f5",),
    "show_desktop": ("win", "d"),
    "switch_window": ("alt", "tab"),
}


@safe
def press_shortcut(action: str) -> str:
    """Presses a keyboard shortcut in the active window.

    Args:
        action: One of: new_tab, new_file, save, select_all, copy, paste, undo, redo, close_tab, refresh, show_desktop, switch_window.
    """
    keys = SHORTCUTS.get(action)
    if not keys:
        return f"Unknown shortcut. Choose from: {', '.join(SHORTCUTS)}"
    pyautogui.hotkey(*keys)
    return f"Pressed {action}"


@safe
def type_text(text: str) -> str:
    """Types text with the keyboard into whatever window is focused, such as Notepad.

    Args:
        text: The exact text to type.
    """
    auto.type_text(text)
    return f"Typed: {text}"


@safe
def take_screenshot() -> str:
    """Takes a screenshot of the whole screen and saves it to the screenshots folder."""
    auto.take_screenshot()
    return "Screenshot saved in the screenshots folder"


@safe
def open_screenshots_folder() -> str:
    """Opens the folder where screenshots are saved."""
    os.makedirs(auto.SCREENSHOT_DIR, exist_ok=True)
    os.startfile(auto.SCREENSHOT_DIR)
    return "Opened the screenshots folder"


@safe
def get_active_window_title() -> str:
    """Gets the title of the window the user is currently using."""
    return auto.get_active_window_title() or "Could not read the active window"


@safe
def change_volume(direction: str) -> str:
    """Changes the computer's speaker volume.

    Args:
        direction: One of "up", "down" or "mute".
    """
    if direction == "up":
        pyautogui.press("volumeup", presses=5)
    elif direction == "down":
        pyautogui.press("volumedown", presses=5)
    elif direction == "mute":
        pyautogui.press("volumemute")
    else:
        return "Direction must be up, down or mute"
    return f"Volume {direction}"


@safe
def scroll_page(direction: str) -> str:
    """Scrolls the active window.

    Args:
        direction: Either "up" or "down".
    """
    pyautogui.scroll(600 if direction == "up" else -600)
    return f"Scrolled {direction}"


ALL_TOOLS = [
    get_current_time_and_date, get_weather, get_news_headlines,
    open_website, search_google, play_on_youtube, open_app,
    set_timer, cancel_all_timers,
    add_note, read_notes, clear_all_notes,
    press_shortcut, type_text, take_screenshot, open_screenshots_folder,
    get_active_window_title, change_volume, scroll_page,
]