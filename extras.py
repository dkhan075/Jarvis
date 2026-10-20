import re
import time
import uuid
import datetime
import threading
import xml.etree.ElementTree as ET

import requests
import pyautogui

from speak import speak
from storage import read, modify

# Change this to your own city
DEFAULT_CITY = "Bengaluru"

NEWS_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

# Running timer threads, keyed by timer id
_timers = {}


# ---------------------------------------------------------------- weather
WEATHER_CODES = {
    0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "rain showers", 81: "rain showers", 82: "heavy rain showers",
    95: "a thunderstorm", 96: "a thunderstorm with hail", 99: "a thunderstorm with hail",
}


def get_weather(city):
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        timeout=8,
    ).json()
    if not geo.get("results"):
        return f"I could not find a city called {city}."

    place = geo["results"][0]
    data = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code",
        },
        timeout=8,
    ).json()["current"]

    desc = WEATHER_CODES.get(data["weather_code"], "unsettled weather")
    return (
        f"In {place['name']} it is {round(data['temperature_2m'])} degrees Celsius "
        f"with {desc}. It feels like {round(data['apparent_temperature'])}, "
        f"and humidity is {data['relative_humidity_2m']} percent."
    )


def weather_command(command):
    city = DEFAULT_CITY
    after = command.split("weather", 1)[1]
    match = re.search(r"\b(?:in|at|for)\s+([a-z ]+)", after)
    if match:
        city = re.sub(r"\b(today|now|right now|tomorrow|please)\b", "", match.group(1)).strip() or DEFAULT_CITY
    try:
        return get_weather(city)
    except Exception as e:
        print(f"Weather error: {e}")
        return "Sorry, I could not get the weather right now."


# ------------------------------------------------------------------- news
def news_command():
    try:
        resp = requests.get(NEWS_URL, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(resp.content)
        headlines = []
        for item in root.iter("item"):
            title = item.findtext("title", "")
            title = title.rsplit(" - ", 1)[0]  # drop the "- Source name" suffix
            headlines.append(title)
            if len(headlines) == 5:
                break
        if not headlines:
            return "I could not find any headlines."
        spoken = ". ".join(f"{i}. {h}" for i, h in enumerate(headlines, 1))
        return "Here are the top headlines. " + spoken
    except Exception as e:
        print(f"News error: {e}")
        return "Sorry, I could not get the news right now."


# ------------------------------------------------------ timers & reminders
UNIT_SECONDS = {"second": 1, "sec": 1, "minute": 60, "min": 60, "hour": 3600, "hr": 3600}


def parse_duration(command):
    """Returns (seconds, spoken_text) or None."""
    m = re.search(r"(\d+)\s*(second|sec|minute|min|hour|hr)s?", command)
    if not m:
        return None
    amount, unit = int(m.group(1)), m.group(2)
    seconds = amount * UNIT_SECONDS[unit]
    word = {"sec": "second", "min": "minute", "hr": "hour"}.get(unit, unit)
    spoken = f"{amount} {word}" + ("s" if amount != 1 else "")
    return seconds, spoken


def _remove_saved_timer(timer_id):
    modify(lambda d: d.update(timers=[t for t in d["timers"] if t["id"] != timer_id]))


def _fire(timer_id, message):
    _timers.pop(timer_id, None)
    _remove_saved_timer(timer_id)
    speak(message)


def start_timer(seconds, message, timer_id=None, save=True):
    timer_id = timer_id or uuid.uuid4().hex
    if save:
        due = time.time() + seconds
        modify(lambda d: d["timers"].append({"id": timer_id, "due": due, "message": message}))
    t = threading.Timer(seconds, _fire, args=(timer_id, message))
    t.daemon = True  # dies with the program (the saved copy survives)
    t.start()
    _timers[timer_id] = t


def restore_timers():
    """Call once at startup: restarts saved timers and reports any that expired while Jarvis was off."""
    now = time.time()
    missed = []
    for saved in read()["timers"]:
        remaining = saved["due"] - now
        if remaining > 0:
            start_timer(remaining, saved["message"], timer_id=saved["id"], save=False)
        else:
            missed.append(saved["message"])

    # Drop the expired ones from the file
    modify(lambda d: d.update(timers=[t for t in d["timers"] if t["id"] in _timers]))

    if missed:
        speak("While I was offline, you missed: " + ". ".join(missed))


def timer_command(command):
    if "cancel" in command:
        count = len(_timers)
        for t in _timers.values():
            t.cancel()
        _timers.clear()
        modify(lambda d: d.update(timers=[]))
        if not count:
            return "You have no active timers."
        return f"Cancelled {count} timer" + ("" if count == 1 else "s")

    duration = parse_duration(command)
    if not duration:
        return "For how long? Say something like, set a timer for 5 minutes."
    seconds, spoken = duration

    if "remind" in command:
        m = re.search(r"remind me (?:to )?(.+?)\s+(?:in|after)\s+\d", command) or \
            re.search(r"remind me (?:in|after)\s+\d+\s*\w+\s+(?:to )?(.+)", command)
        task = m.group(1).strip() if m else "do your task"
        start_timer(seconds, f"Reminder: {task}")
        return f"Okay, I will remind you to {task} in {spoken}"

    start_timer(seconds, f"Time is up! Your {spoken} timer has finished.")
    return f"Timer set for {spoken}"


# ------------------------------------------------------------------ notes
def add_note(text):
    entry = {"text": text, "created": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")}
    modify(lambda d: d["notes"].append(entry))
    return f"Noted: {text}"


def read_notes():
    notes = read()["notes"]
    if not notes:
        return "You have no notes yet."
    recent = notes[-10:]  # read at most the 10 newest
    spoken = ". ".join(f"Note {i}: {n['text']}" for i, n in enumerate(recent, 1))
    count = len(notes)
    return f"You have {count} note" + ("" if count == 1 else "s") + ". " + spoken


def clear_notes():
    modify(lambda d: d.update(notes=[]))
    return "All notes cleared."


def notes_command(command):
    # Whole-word matching, so "notepad" is NOT mistaken for "note"
    if re.search(r"\b(clear|delete|erase)\b.*\bnotes?\b", command):
        return clear_notes()

    if re.search(r"\b(read|show|list|what are)\b.*\bnotes\b|\bmy notes\b", command):
        return read_notes()

    m = re.search(r"\b(?:take a note|make a note|add a note|add note|note down|note)\b[:,]?\s*(?:that\s+)?(.+)", command)
    if m:
        return add_note(m.group(1).strip())
    return None


# ------------------------------------------------------- open any app
def open_any_app(command):
    """Uses the Windows Start menu search, so it works for any installed app."""
    name = re.sub(r"\b(open|launch|start|the|app|application|please)\b", "", command).strip()
    if not name:
        return "Which app should I open?"
    pyautogui.press("win")
    time.sleep(0.8)
    pyautogui.write(name, interval=0.05)
    time.sleep(1.0)
    pyautogui.press("enter")
    return f"Trying to open {name}"


# ------------------------------------------------------------- dispatcher
def handle_extras(command):
    """Weather, news, timers, reminders, notes. Returns text to speak, or None."""
    if "weather" in command:
        return weather_command(command)
    if "news" in command or "headlines" in command:
        return news_command()
    if "timer" in command or "remind me" in command:
        return timer_command(command)
    if re.search(r"\bnotes?\b", command):
        return notes_command(command)
    return None