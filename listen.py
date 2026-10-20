import speech_recognition as sr
from ui import status

recognizer = sr.Recognizer()


def listen():
    with sr.Microphone() as source:
        print("Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        status("Listening")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            status("Idle")
            return ""

    try:
        print("Recognizing...")
        status("Recognizing")
        text = recognizer.recognize_google(audio, language="en-in")
        print(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError:
        print("Speech service unavailable (check internet)")
        return ""
    finally:
        status("Idle")


if __name__ == "__main__":
    listen()