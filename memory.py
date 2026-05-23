from datetime import datetime
from speech import speak

NOTES_FILE = "notes.txt"

def write_note(text):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"[{timestamp}] {text}\n")
    speak("I have saved your note")


def read_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file_handle:
            return [line.strip() for line in file_handle if line.strip()]
    except FileNotFoundError:
        return []
