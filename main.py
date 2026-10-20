from speak import speak
from listen import listen
from commands import handle_command
from brain import ask_gemini
from extras import restore_timers
from ui import log, status

WAKE_WORD = "jarvis"

# True: Gemini chooses tools (function calling). False: keyword router only.
USE_AI_TOOLS = True


def process(command):
    """Gemini picks the tool to run; the keyword router is the fallback."""
    status("Thinking")
    if USE_AI_TOOLS:
        response = ask_gemini(command)
        if response:
            return response
        print("Gemini unavailable, using the keyword router instead.")

    response = handle_command(command)
    if response is None:
        response = "Sorry, I can't reach my AI brain right now, and I don't know that command offline."
    return response


def main():
    speak("Jarvis is online. Say my name to wake me up.")
    restore_timers()  # bring back timers saved before the last shutdown
    while True:
        try:
            heard = listen()
            if not heard:
                continue

            if WAKE_WORD in heard:
                command = heard.replace(WAKE_WORD, "").strip()

                if not command:
                    speak("Yes?")
                    command = listen().replace(WAKE_WORD, "").strip()
                    if not command:
                        speak("I didn't catch that.")
                        continue

                log("you", command)

                if "exit" in command or "stop" in command or "goodbye" in command:
                    speak("Goodbye!")
                    break

                speak(process(command))

        except KeyboardInterrupt:
            print("\nShutting down Jarvis.")
            break
        except Exception as e:
            # Never let one bad command crash the whole assistant
            print(f"Error: {e}")
            try:
                speak("Sorry, something went wrong.")
            except Exception:
                pass


if __name__ == "__main__":
    main()