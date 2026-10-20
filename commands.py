import webbrowser
import datetime
from urllib.parse import quote_plus

from extras import handle_extras, open_any_app
from automation import handle_automation

# Websites Jarvis can open by name
SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "linkedin": "https://www.linkedin.com",
    "stack overflow": "https://stackoverflow.com",
}


def handle_command(command):
    """
    Returns a string for Jarvis to speak if the command was handled,
    or None if it wasn't (so Gemini can take over).
    """

    # 0a. Weather, news, timers, reminders (checked first so "timer" is not read as "time")
    result = handle_extras(command)
    if result:
        return result

    # 0b. Desktop automation (typing, screenshots, volume, apps...)
    result = handle_automation(command)
    if result:
        return result

    # 1. Time
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"It is {now}"

    # 2. Date
    if "date" in command or "what day" in command:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        return f"Today is {today}"

    # 3. Search Google
    if command.startswith("search"):
        query = command.replace("search for", "").replace("search", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            return f"Searching Google for {query}"
        return "What should I search for?"

    # 4. Play on YouTube
    if command.startswith("play"):
        query = command.replace("play", "", 1).strip()
        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            return f"Playing {query} on YouTube"
        return "What should I play?"

    # 5. Open a website, otherwise try any installed app
    if command.startswith("open") or command.startswith("launch"):
        for name, url in SITES.items():
            if name in command:
                webbrowser.open(url)
                return f"Opening {name}"
        return open_any_app(command)

    # Not handled
    return None