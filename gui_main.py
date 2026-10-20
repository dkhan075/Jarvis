import threading

import main as jarvis
from speak import speak
from ui import JarvisUI, log, request_quit


def handle_typed(text):
    """Runs a typed command on its own thread so the window never freezes."""
    def work():
        log("you", text)
        try:
            speak(jarvis.process(text.lower()))
        except Exception as e:
            print(f"Error: {e}")
            speak("Sorry, something went wrong.")
    threading.Thread(target=work, daemon=True).start()


def run_jarvis():
    jarvis.main()       # returns when you say "goodbye"
    request_quit()      # then close the window


if __name__ == "__main__":
    app = JarvisUI(on_text_command=handle_typed)
    threading.Thread(target=run_jarvis, daemon=True).start()
    app.run()