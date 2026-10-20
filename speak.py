import os
import uuid
import tempfile
import threading

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import pyttsx3
from gtts import gTTS

from ui import log, status

# True = natural Google voice (needs internet), falls back to offline voice
USE_ONLINE_VOICE = False

_mixer_ready = False
_speak_lock = threading.Lock()


def _speak_online(text):
    """Natural-sounding voice using gTTS + pygame playback."""
    global _mixer_ready
    if not _mixer_ready:
        pygame.mixer.init()
        _mixer_ready = True

    path = os.path.join(tempfile.gettempdir(), f"jarvis_{uuid.uuid4().hex}.mp3")
    try:
        gTTS(text=text, lang="en", tld="co.in").save(path)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        try:
            pygame.mixer.music.unload()
            os.remove(path)
        except Exception:
            pass


def _speak_offline(text):
    """Offline robotic voice. Engine is created each time to avoid Windows silence bug."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.say(text)
    engine.runAndWait()


def speak(text):
    print(f"Jarvis: {text}")
    log("jarvis", text)
    with _speak_lock:
        status("Speaking")
        try:
            if USE_ONLINE_VOICE:
                try:
                    _speak_online(text)
                    return
                except Exception as e:
                    print(f"(Online voice failed, using offline voice: {e})")
            _speak_offline(text)
        finally:
            status("Idle")


if __name__ == "__main__":
    speak("Hello, I am Jarvis. Setup is working.")