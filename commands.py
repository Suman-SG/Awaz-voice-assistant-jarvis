import datetime
import time
import webbrowser
from urllib.parse import quote_plus

import config
from speech import speak, listen
from memory import write_note, read_notes
from apps import open_app
from history import write_command_history
from nlp import resolve_app, resolve_website

try:
    import win32api
    import win32clipboard
    import win32con
except Exception:
    win32api = None
    win32clipboard = None
    win32con = None


ACTIVE_TARGET = {"kind": None, "name": None}


def set_active_target(kind=None, name=None):
    ACTIVE_TARGET["kind"] = kind
    ACTIVE_TARGET["name"] = name


def get_active_target():
    return dict(ACTIVE_TARGET)


def clear_active_target():
    set_active_target()


def build_search_url(site_name, query):
    encoded_query = quote_plus(query)

    if site_name == "google":
        return f"https://www.google.com/search?q={encoded_query}"

    if site_name == "youtube":
        return f"https://www.youtube.com/results?search_query={encoded_query}"

    if site_name == "whatsapp":
        return "https://web.whatsapp.com"

    return None


def copy_text_to_clipboard(text):
    if win32clipboard is not None:
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
        finally:
            win32clipboard.CloseClipboard()
        return True

    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


def press_ctrl_v_and_enter(press_enter=False):
    if win32api is None or win32con is None:
        return False

    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord("V"), 0, 0, 0)
    win32api.keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

    if press_enter:
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

    return True


def collect_dictation(prompt_text="Start speaking now.", single_shot=True):
    speak(prompt_text)

    stop_words = ["send it", "send", "done", "stop", "finish"]
    parts = []
    silence_count = 0

    while True:
        line = listen(timeout=config.LISTEN_TIMEOUT, phrase_time_limit=config.NOTE_PHRASE_TIME_LIMIT)

        if not line:
            silence_count += 1
            if single_shot and parts and silence_count >= 2:
                break
            if silence_count >= 4:
                break
            continue

        silence_count = 0
        cleaned = line.lower().strip()

        if any(stop_word == cleaned or stop_word in cleaned for stop_word in stop_words):
            break

        parts.append(cleaned)
        speak("Added")

        if single_shot:
            break

        if len(" ".join(parts)) >= config.NOTE_MAX_LENGTH:
            speak("That is long enough. I will use this text now.")
            break

    return " ".join(parts).strip()


def confirm_and_launch(label, launch_callback):
    speak(f"Did you mean {label}? Say yes to open it or no to cancel.")
    response = listen(timeout=6, phrase_time_limit=3).lower().strip()

    if any(word in response for word in ["yes", "yeah", "sure", "okay", "ok"]):
        launch_callback()
        return True

    if not response:
        speak(f"No response detected. Opening {label}.")
        launch_callback()
        return True

    if any(word in response for word in ["no", "nope", "cancel", "don't", "do not"]):
        speak("Okay, not opening it.")
        return False

    speak("I did not catch that clearly.")
    return False


def launch_website(name):
    websites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "spotify": "https://www.spotify.com",
        "whatsapp": "https://web.whatsapp.com",
        "github": "https://www.github.com",
        "linkedin": "https://www.linkedin.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "x": "https://x.com",
        "reddit": "https://www.reddit.com",
        "gmail": "https://mail.google.com",
        "drive": "https://drive.google.com",
        "maps": "https://www.google.com/maps",
        "news": "https://news.google.com",
        "amazon": "https://www.amazon.com",
        "wikipedia": "https://www.wikipedia.org",
    }

    url = websites.get(name)
    if url:
        set_active_target("website", name)
        webbrowser.open(url)
        speak(f"Opening {name}")


def open_launch_target(text, kind):
    if kind == "app":
        name, score = resolve_app(text)
        if not name:
            speak("Which application should I open?")
            return

        if score >= config.MATCH_THRESHOLD:
            set_active_target("app", name)
            open_app(name)
            return

        confirm_and_launch(name, lambda: (set_active_target("app", name), open_app(name)))
        return

    if kind == "website":
        name, score = resolve_website(text)
        if not name:
            speak("Which website should I open?")
            return

        if score >= config.MATCH_THRESHOLD:
            launch_website(name)
            return

        confirm_and_launch(name, lambda: launch_website(name))


def start_website_search(site_name):
    if site_name not in {"google", "youtube"}:
        speak("I can only search Google or YouTube right now.")
        return True

    set_active_target("website", site_name)
    speak(f"What should I search on {site_name}?")

    query_text = collect_dictation(prompt_text=f"Tell me the topic for {site_name}.", single_shot=True)
    if not query_text:
        speak("I did not hear the topic.")
        return True

    # Confirm before searching
    speak(f"I heard {query_text}. Should I search {site_name} for that? Say yes to proceed or no to cancel.")
    response = listen(timeout=6, phrase_time_limit=4)
    response = (response or "").lower()

    if any(w in response for w in ["yes", "yeah", "sure", "please", "do it", "ok", "okay"]):
        speak(f"Searching {site_name} for {query_text} now.")
        url = build_search_url(site_name, query_text)
        if url:
            webbrowser.open(url)
        return True

    speak("Okay, cancelled.")
    return True


def dictate_into_active_target():
    target = get_active_target()

    if not target["kind"] or not target["name"]:
        speak("Open Google, Notepad, or WhatsApp first.")
        return True

    dictated_text = collect_dictation(single_shot=True)

    if not dictated_text:
        speak("I did not hear any text to use.")
        return True

    if target["kind"] == "website" and target["name"] in {"google", "youtube", "whatsapp"}:
        url = build_search_url(target["name"], dictated_text)

        if target["name"] in {"google", "youtube"} and url:
            speak(f"I heard {dictated_text}. Searching {target['name']} now.")
            webbrowser.open(url)
            return True

        if target["name"] == "whatsapp":
            webbrowser.open(url)
            time.sleep(2)
            if copy_text_to_clipboard(dictated_text) and press_ctrl_v_and_enter(press_enter=True):
                speak("I typed and sent the message in WhatsApp Web. Make sure the chat is open.")
            else:
                speak("I opened WhatsApp Web, but I could not paste the message automatically.")
            return True

    if target["kind"] == "app" and target["name"] == "notepad":
        open_app("notepad")
        time.sleep(1)

        if copy_text_to_clipboard(dictated_text) and press_ctrl_v_and_enter(press_enter=False):
            speak("I typed the text into Notepad.")
        else:
            speak("I opened Notepad, but I could not paste the text automatically.")

        return True

    if target["kind"] == "app" and target["name"] == "whatsapp":
        open_app("whatsapp")
        time.sleep(2)

        if copy_text_to_clipboard(dictated_text) and press_ctrl_v_and_enter(press_enter=True):
            speak("I typed and sent the message in WhatsApp.")
        else:
            speak("I opened WhatsApp, but I could not paste the message automatically.")

        return True

    speak(f"I can hear the text, but I do not yet know how to type into {target['name']}.")
    return True


def execute_intent(intent, text):
    write_command_history(text, intent)

    if intent == "open_google":
        set_active_target("website", "google")
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif intent == "open_youtube":
        set_active_target("website", "youtube")
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")

    elif intent == "search_youtube":
        return start_website_search("youtube")

    elif intent == "search_google":
        return start_website_search("google")

    elif intent == "get_time":
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")

    elif intent == "write_note":
        speak("Note mode activated. Start speaking. Say 'stop note' to finish.")

        stop_words = ["stop note", "stop writing", "end note", "finish note"]
        ignore_words = ["jarvis", "hey jarvis", "ok jarvis"]

        notes = []

        while True:
            line = listen(timeout=8, phrase_time_limit=6)

            if not line:
                continue

            line = line.lower().strip()

            if any(stop_word in line for stop_word in stop_words):
                break

            for ignore_word in ignore_words:
                line = line.replace(ignore_word, "").strip()

            if len(line) < 3:
                continue

            notes.append(line)
            speak("Added")

            if len(" ".join(notes)) > 200:
                speak("Note too long. Saving now.")
                break

        if notes:
            final_note = " ".join(notes).strip()
            write_note(final_note)
            speak("Note saved. Exiting note mode.")
        else:
            speak("No note recorded.")

    elif intent == "read_notes":
        notes = read_notes()
        if not notes:
            speak("You do not have any notes yet.")
        else:
            speak(f"You have {len(notes)} notes.")
            for note in notes[-5:]:
                speak(note)

    elif intent == "open_app":
        open_launch_target(text, kind="app")

    elif intent == "open_website":
        open_launch_target(text, kind="website")

    elif intent == "dictate_active":
        return dictate_into_active_target()

    elif intent == "test_speech":
        # Speak a short test phrase and list available voices to the console
        try:
            from config import load_settings
            settings = load_settings()
            phrase = settings.get("SPEECH_TEST_PHRASE", "This is a speech test.")
        except Exception:
            phrase = "This is a speech test."

        speak(phrase)

        try:
            voices = []
            engine = None
            import pyttsx3
            engine = pyttsx3.init("sapi5")
            for v in engine.getProperty("voices"):
                voices.append(v.name)
            print("Available voices:", voices)
        except Exception as e:
            print("Could not enumerate voices:", e)

        return True

    elif intent == "diagnose_audio":
        # Save TTS output to a WAV file and attempt to play it via winsound
        try:
            from config import load_settings
            settings = load_settings()
            phrase = settings.get("SPEECH_TEST_PHRASE", "This is an audio diagnostic test.")
        except Exception:
            phrase = "This is an audio diagnostic test."

        speak("Running audio diagnostics. I will speak a test phrase and then play it back.")

        try:
            import pyttsx3
            import tempfile
            import os

            engine = pyttsx3.init("sapi5")
            engine.setProperty("rate", config.SPEECH_RATE)
            engine.setProperty("volume", config.SPEECH_VOLUME)
            voices = engine.getProperty("voices")
            if voices:
                voice_index = min(max(config.SPEECH_VOICE_INDEX, 0), len(voices) - 1)
                engine.setProperty("voice", voices[voice_index].id)

            wav_path = os.path.join(tempfile.gettempdir(), "jarvis_tts_test.wav")
            engine.save_to_file(phrase, wav_path)
            engine.runAndWait()

            speak("Saved test audio. Now attempting to play the saved WAV file.")

            try:
                import winsound
                winsound.PlaySound(wav_path, winsound.SND_FILENAME)
                speak("Playback finished. Did you hear the WAV playback?")
            except Exception as e:
                print("winsound playback failed:", e)
                print('Attempting fallback player via os.startfile')
                try:
                    os.startfile(wav_path)
                    speak("I opened the WAV file with the default player. Please check if you hear it now.")
                except Exception as e2:
                    print('startfile failed:', e2)
                    speak(f"I could not play the WAV automatically. The test file is at {wav_path}")

        except Exception as e:
            print("Audio diagnostic failed:", e)
            speak("Audio diagnostic failed. Check the console for details.")

        return True

    elif intent == "shutdown":
        speak("Are you sure you want to shut down the system? Please say 'confirm shutdown' to proceed.")

    elif intent == "restart":
        speak("Are you sure you want to restart the system? Please say 'confirm restart' to proceed.")

    elif intent == "confirm_shutdown":
        speak("Shutting down the system now.")
        import os
        os.system("shutdown /s /t 1")

    elif intent == "confirm_restart":
        speak("Restarting the system now.")
        import os
        os.system("shutdown /r /t 1")

    elif intent == "exit":
        speak("Goodbye")
        clear_active_target()
        return False

    else:
        speak("Sorry, I did not understand")

    return True