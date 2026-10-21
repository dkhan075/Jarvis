# Jarvis: Voice-Controlled AI Assistant

A Windows desktop voice assistant built in Python. Say "Jarvis" followed by a request and it listens, decides what to do, acts on your computer, and speaks back. Google Gemini chooses which tool to run using **function calling**, and a keyword router takes over when the AI is unreachable.

<!-- Add a screenshot of the Jarvis window here -->
<!-- ![Jarvis window](docs/screenshot.png) -->

<!-- Add a link to your demo video here -->
<!-- [Watch the demo](your-video-link) -->

## Features

- **Wake-word activation:** responds only when you say "Jarvis"
- **LLM tool use:** Gemini reads each request and picks from 19 tools (weather, news, timers, notes, web, typing, screenshots, volume, shortcuts, app launching and more), including requests that need several tools at once
- **Graceful fallback:** if Gemini is unreachable or rate-limited, a rule-based keyword router handles basic commands
- **Two-voice output:** natural online voice (gTTS) with automatic fallback to an offline voice (pyttsx3)
- **Desktop automation:** PyAutoGUI and PyGetWindow for typing, screenshots, reading the active window title, volume, scrolling, shortcuts, and launching any installed app
- **Persistent memory:** notes and timers are saved to disk, so reminders survive restarts and missed ones are announced on startup
- **GUI:** a Tkinter window showing the conversation and live status (listening, thinking, speaking)
- **Packaged app:** builds into a standalone `Jarvis.exe` with PyInstaller

## How it works

```
Microphone -> SpeechRecognition -> wake word check
                                        |
                                  Gemini (function calling)
                               chooses and runs tools in tools.py
                                        |
                      weather / news / timers / notes / web /
                      typing / screenshots / volume / apps ...
                                        |
                              spoken reply -> gTTS or pyttsx3 -> Speaker

If Gemini is unavailable: keyword router (commands.py) handles basic commands.
```

Each tool is a plain Python function. Gemini reads its name, type hints and docstring to decide when to call it, so the docstrings in `tools.py` act as instructions to the model. Tool output is treated as data, never as instructions, to reduce prompt-injection risk from web content such as headlines.

## Download

Grab the latest Windows build from the [Releases page](https://github.com/dkhan075/Jarvis/releases/latest).
Extract it, add your own `.env` file next to `Jarvis.exe` (see `.env.example`), and run it.

If Windows blocks the app (Smart App Control), turn that setting off temporarily or run from source using the setup steps below.

## Setup

1. Clone the repo and create a virtual environment:

```
git clone <your-repo-url>
cd jarvis
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Get a free API key from [Google AI Studio](https://aistudio.google.com/) and create a `.env` file (see `.env.example`):

```
GEMINI_API_KEY=your_key_here
```

4. Run it:

```
python gui_main.py     # with the window
python main.py         # terminal only
```

Set `USE_AI_TOOLS = False` in `main.py` to run with the keyword router only.

## Example requests

| Say | What happens |
|---|---|
| "Jarvis what's the weather in Mumbai" | Gemini calls the weather tool and speaks the result |
| "Jarvis remind me to call mom in half an hour" | Gemini converts the time and sets a saved reminder |
| "Jarvis open notepad and type hello world" | Two tools run in sequence |
| "Jarvis take a note that the demo is on Friday" | Saves a note to disk |
| "Jarvis take a screenshot" | Saves a PNG to `screenshots/` |
| "Jarvis explain recursion" | Answered directly by Gemini |
| "Jarvis goodbye" | Shuts down |

## Build the .exe

```
pip install pyinstaller
build.bat              # console build, errors are visible
build.bat windowed     # final build, no console window
```

The app is created in `dist\Jarvis\`. Put your own `.env` file next to `Jarvis.exe`. The API key is read at runtime and is never bundled into the build.

## Project structure

```
main.py         wake-word loop and request processing
gui_main.py     starts Jarvis with the Tkinter window
ui.py           the window and thread-safe update queue
listen.py       microphone input and speech-to-text
speak.py        text-to-speech with online/offline fallback
brain.py        Gemini client with function calling
tools.py        the tools Gemini can call
commands.py     keyword router (fallback)
automation.py   PyAutoGUI and PyGetWindow desktop control
extras.py       weather, news, timers, reminders, notes, app launcher
storage.py      saved notes and timers (JSON)
paths.py        finds the right data folder for scripts and the .exe
build.bat       PyInstaller build script
```

## Tech stack

Python, Google Gemini API (function calling), SpeechRecognition, PyAudio, gTTS, pyttsx3, pygame, PyAutoGUI, PyGetWindow, Pillow, Tkinter, Requests, PyInstaller

## Known limitations

- Windows only (app launching and some shortcuts are Windows-specific)
- Speech recognition and gTTS need an internet connection
- The free Gemini tier has rate limits, in which case the keyword router takes over
- Recognized speech arrives without punctuation, so typed text is only capitalized at the start
