import os
import shutil
import subprocess
from difflib import SequenceMatcher
from pathlib import Path

from speech import speak

APPS = {
    "calculator": "calc.exe",
    "notepad": "notepad.exe",
    "clock": "ms-clock:",
    "calendar": "outlookcal:",
    "paint": "mspaint.exe",
    "camera": "microsoft.windows.camera:",
    "photos": "ms-photos:",
    "settings": "ms-settings:",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "vscode": "code.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "spotify": "spotify.exe",
    "whatsapp": "WhatsApp.exe",
    "discord": "Discord.exe",
    "steam": "steam.exe"
}


START_MENU_ROOTS = [
    Path(os.environ.get("ProgramData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
]


def normalize_label(text):
    return " ".join("".join(character.lower() if character.isalnum() else " " for character in text).split())


def discover_installed_apps(limit=250):
    discovered = {}

    for root in START_MENU_ROOTS:
        if not root.exists():
            continue

        for shortcut in root.rglob("*.lnk"):
            label = normalize_label(shortcut.stem)
            if label and label not in discovered:
                discovered[label] = str(shortcut)

            if len(discovered) >= limit:
                return discovered

    return discovered


def build_app_index():
    index = {}

    for app_name, target in APPS.items():
        index[normalize_label(app_name)] = target

    for app_name, shortcut_path in discover_installed_apps().items():
        index.setdefault(app_name, shortcut_path)

    return index


APP_INDEX = build_app_index()


def resolve_launch_target(app_name):
    normalized_name = normalize_label(app_name)

    if normalized_name in APP_INDEX:
        return normalized_name, APP_INDEX[normalized_name]

    best_name = None
    best_score = 0.0

    for candidate_name in APP_INDEX:
        score = SequenceMatcher(None, normalized_name, candidate_name).ratio()
        if score > best_score:
            best_score = score
            best_name = candidate_name

    if best_name and best_score >= 0.6:
        return best_name, APP_INDEX[best_name]

    return None, None

def open_app(app_name):
    resolved_name, target = resolve_launch_target(app_name)

    if not target:
        speak("Application not found")
        return

    try:
        if os.path.exists(target) and Path(target).suffix.lower() in {".lnk", ".url", ".appref-ms"}:
            os.startfile(target)
        elif ":" in target and not target.lower().endswith(".exe"):
            os.startfile(target)
        else:
            resolved_path = shutil.which(target) or target
            subprocess.Popen([resolved_path], shell=False)

        speak(f"Opening {resolved_name}")
    except Exception:
        speak(f"Sorry, I could not open {app_name}")
