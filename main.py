import time

from config import load_settings
from speech import speak, listen
from nlp import detect_intent
from commands import execute_intent, get_active_target

DIRECT_COMMAND_INTENTS = {
    "open_google",
    "search_google",
    "search_youtube",
    "open_youtube",
    "open_app",
    "open_website",
    "get_time",
    "write_note",
    "read_notes",
    "chat",
}

DICTATION_TRIGGERS = {
    "write",
    "type",
    "search",
    "send",
    "send it",
    "type it",
    "write it",
}

def remove_wake_word(text):
    settings = load_settings()
    for word in settings["WAKE_WORDS"]:
        text = text.replace(word, "")
    return text.strip()

def main():
    speak("Jarvis online")

    running = True
    paused_notice_shown = False
    while running:
        settings = load_settings()

        if not settings.get("ASSISTANT_ENABLED", True):
            if not paused_notice_shown:
                print("Assistant paused. Enable it from the web panel to listen.")
                paused_notice_shown = True
            time.sleep(0.75)
            continue

        paused_notice_shown = False

        text = listen(timeout=settings["LISTEN_TIMEOUT"])

        if not text:
            continue

        print("Heard:", text)

        direct_intent = detect_intent(text)
        if direct_intent in DIRECT_COMMAND_INTENTS and not any(word in text for word in settings["WAKE_WORDS"]):
            running = execute_intent(direct_intent, text)
            continue

        active_target = get_active_target()
        if active_target.get("name") and any(trigger in text for trigger in DICTATION_TRIGGERS):
            running = execute_intent("dictate_active", text)
            continue

        if any(word in text for word in settings["WAKE_WORDS"]):
            command_text = remove_wake_word(text)

            if not command_text:
                speak("Yes")
                command_text = listen(timeout=settings["COMMAND_TIMEOUT"], phrase_time_limit=settings["COMMAND_TIMEOUT"])

                if not command_text:
                    continue

                print("Command text:", command_text)

            intent = detect_intent(command_text)
            running = execute_intent(intent, command_text)

if __name__ == "__main__":
    main()
