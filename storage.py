import json
import os
import threading

from paths import app_dir

# Saved next to your code (or next to Jarvis.exe)
DATA_FILE = os.path.join(app_dir(), "jarvis_data.json")
_lock = threading.Lock()


def _read():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data.setdefault("notes", [])
    data.setdefault("timers", [])
    return data


def read():
    """Returns the saved data: {'notes': [...], 'timers': [...]}."""
    with _lock:
        return _read()


def modify(change):
    """
    Loads the data, lets `change(data)` edit it, then saves it safely.
    The lock makes this safe when a timer thread and the main loop save together.
    """
    with _lock:
        data = _read()
        result = change(data)
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, DATA_FILE)  # write to a temp file first so a crash can't corrupt the data
        return result