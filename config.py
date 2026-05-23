import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "assistant_settings.json"

DEFAULT_SETTINGS = {
    "ASSISTANT_ENABLED": True,
    "WAKE_WORDS": ["jarvis", "hey jarvis", "ok jarvis"],
    "LISTEN_TIMEOUT": 8,
    "COMMAND_TIMEOUT": 6,
    "NOTE_PHRASE_TIME_LIMIT": 6,
    "SPEECH_RATE": 170,
    "SPEECH_VOLUME": 1.0,
    "SPEECH_VOICE_INDEX": 0,
    "SPEAK_BUFFER_DELAY": 0.8,
    "SPEECH_TEST_PHRASE": "This is a quick speech test. If you hear this, Jarvis TTS is working.",
    "NOTE_MAX_LENGTH": 200,
    "MATCH_THRESHOLD": 50,
}


def load_settings():
    settings = dict(DEFAULT_SETTINGS)

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file_handle:
                saved_settings = json.load(file_handle)
            if isinstance(saved_settings, dict):
                settings.update(saved_settings)
        except Exception:
            pass

    settings["WAKE_WORDS"] = [word.strip().lower() for word in settings.get("WAKE_WORDS", []) if word.strip()]
    settings["WAKE_WORDS"] = settings["WAKE_WORDS"] or DEFAULT_SETTINGS["WAKE_WORDS"]
    settings["ASSISTANT_ENABLED"] = bool(settings.get("ASSISTANT_ENABLED", DEFAULT_SETTINGS["ASSISTANT_ENABLED"]))
    settings["LISTEN_TIMEOUT"] = int(settings.get("LISTEN_TIMEOUT", DEFAULT_SETTINGS["LISTEN_TIMEOUT"]))
    settings["COMMAND_TIMEOUT"] = int(settings.get("COMMAND_TIMEOUT", DEFAULT_SETTINGS["COMMAND_TIMEOUT"]))
    settings["NOTE_PHRASE_TIME_LIMIT"] = int(settings.get("NOTE_PHRASE_TIME_LIMIT", DEFAULT_SETTINGS["NOTE_PHRASE_TIME_LIMIT"]))
    settings["SPEECH_RATE"] = int(settings.get("SPEECH_RATE", DEFAULT_SETTINGS["SPEECH_RATE"]))
    settings["SPEECH_VOLUME"] = float(settings.get("SPEECH_VOLUME", DEFAULT_SETTINGS["SPEECH_VOLUME"]))
    settings["SPEECH_VOICE_INDEX"] = int(settings.get("SPEECH_VOICE_INDEX", DEFAULT_SETTINGS["SPEECH_VOICE_INDEX"]))
    settings["SPEAK_BUFFER_DELAY"] = float(settings.get("SPEAK_BUFFER_DELAY", DEFAULT_SETTINGS["SPEAK_BUFFER_DELAY"]))
    settings["NOTE_MAX_LENGTH"] = int(settings.get("NOTE_MAX_LENGTH", DEFAULT_SETTINGS["NOTE_MAX_LENGTH"]))
    settings["MATCH_THRESHOLD"] = int(settings.get("MATCH_THRESHOLD", DEFAULT_SETTINGS["MATCH_THRESHOLD"]))

    return settings


def save_settings(updated_settings):
    settings = load_settings()
    settings.update(updated_settings)

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file_handle:
        json.dump(settings, file_handle, indent=2)

    globals().update(settings)
    return settings


_runtime_settings = load_settings()
globals().update(_runtime_settings)
