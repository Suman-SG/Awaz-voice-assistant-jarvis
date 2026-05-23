from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
COMMAND_HISTORY_FILE = BASE_DIR / "command_history.txt"


def write_command_history(command_text, intent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(COMMAND_HISTORY_FILE, "a", encoding="utf-8") as file_handle:
        file_handle.write(f"[{timestamp}] {intent}: {command_text}\n")


def read_command_history(limit=20):
    if not COMMAND_HISTORY_FILE.exists():
        return []

    with open(COMMAND_HISTORY_FILE, "r", encoding="utf-8") as file_handle:
        lines = [line.strip() for line in file_handle if line.strip()]

    return lines[-limit:]
