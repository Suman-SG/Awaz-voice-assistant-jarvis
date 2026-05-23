import re
from difflib import SequenceMatcher

from apps import discover_installed_apps


INTENTS = {
    "search_google": ["search google", "google search", "search on google", "find on google"],
    "search_youtube": ["search youtube", "youtube search", "search on youtube", "find on youtube"],
    "open_google": ["open google", "google"],
    "open_youtube": ["open youtube", "youtube"],
    "open_website": ["open spotify", "open github", "open linkedin"],
    "open_app": ["open calculator", "open notepad", "open clock", "open calendar"],
    "get_time": ["time"],
    "write_note": ["take note", "write note", "remember this"],
    "read_notes": ["read notes", "my notes"],
    "test_speech": ["test speech", "speak test", "voice test", "test tts", "test voice"],
    "diagnose_audio": ["i can't hear", "i cannot hear", "audio test", "sound test", "audio diagnostics", "diagnose audio"],
    "shutdown": ["shutdown", "shut down"],
    "restart": ["restart"],
    "confirm_shutdown": ["confirm shutdown"],
    "confirm_restart": ["confirm restart"],
    "chat": ["how are you", "who are you"],
    "exit": ["exit", "quit", "stop", "goodbye", "close jarvis"],
}


def normalize_text(text):
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def detect_intent(text):
    normalized_text = normalize_text(text)

    for intent, keywords in INTENTS.items():
        for phrase in keywords:
            normalized_phrase = normalize_text(phrase)
            if normalized_phrase and normalized_phrase in normalized_text:
                return intent
    return "unknown"


def score_match(text, phrase):
    normalized_text = normalize_text(text)
    normalized_phrase = normalize_text(phrase)

    if not normalized_text or not normalized_phrase:
        return 0

    ratio_score = SequenceMatcher(None, normalized_text, normalized_phrase).ratio()
    token_overlap = len(set(normalized_text.split()) & set(normalized_phrase.split())) / max(len(normalized_phrase.split()), 1)
    return int(round(max(ratio_score, token_overlap) * 100))


def resolve_best_match(text, corpus):
    best_name = None
    best_score = 0

    for name, aliases in corpus.items():
        for alias in aliases:
            score = score_match(text, alias)
            if score > best_score:
                best_score = score
                best_name = name

    return best_name, best_score


def resolve_app(text):
    corpus = {
        "calculator": ["calculator", "calc", "open calculator", "launch calculator"],
        "notepad": ["notepad", "text pad", "open notepad", "launch notepad"],
        "clock": ["clock", "timer", "alarm", "open clock", "launch clock"],
        "calendar": ["calendar", "planner", "schedule", "open calendar"],
        "paint": ["paint", "mspaint", "drawing app"],
        "camera": ["camera", "webcam"],
        "photos": ["photos", "gallery", "images"],
        "settings": ["settings", "system settings"],
        "file explorer": ["file explorer", "explorer", "files"],
        "task manager": ["task manager", "process manager", "tasks"],
        "command prompt": ["command prompt", "cmd", "terminal"],
        "powershell": ["powershell", "shell"],
        "vscode": ["vscode", "visual studio code", "code editor"],
        "chrome": ["chrome", "google chrome", "browser"],
        "edge": ["edge", "microsoft edge", "browser"],
        "spotify": ["spotify", "music"],
        "whatsapp": ["whatsapp", "chat"],
        "discord": ["discord", "chat app"],
        "steam": ["steam", "games"],
    }

    for app_name in discover_installed_apps().keys():
        corpus.setdefault(app_name, [app_name])

    return resolve_best_match(text, corpus)


def resolve_website(text):
    return resolve_best_match(text, {
        "google": ["google", "search google", "open google"],
        "youtube": ["youtube", "video", "open youtube"],
        "youtube_search": ["search youtube", "youtube search", "search on youtube", "find on youtube"],
        "spotify": ["spotify", "music", "open spotify"],
        "whatsapp": ["whatsapp", "whatsapp web", "open whatsapp", "open whatsapp web"],
        "github": ["github", "code repo", "open github"],
        "linkedin": ["linkedin", "jobs", "open linkedin"],
        "facebook": ["facebook", "fb", "open facebook"],
        "instagram": ["instagram", "insta", "open instagram"],
        "x": ["x", "twitter", "open x", "open twitter"],
        "reddit": ["reddit", "forum", "open reddit"],
        "gmail": ["gmail", "email", "mail", "open gmail"],
        "drive": ["google drive", "drive", "open drive"],
        "maps": ["google maps", "maps", "navigation", "open maps"],
        "news": ["news", "google news", "open news"],
        "amazon": ["amazon", "shopping", "open amazon"],
        "wikipedia": ["wikipedia", "wiki", "open wikipedia"],
    })
