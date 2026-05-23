# Awaz Voice Assistant (Jarvis)

Awaz Voice Assistant is a Windows-focused voice assistant built with Python, speech recognition, and a small Flask dashboard. It listens for wake words, recognizes common commands, speaks responses, launches apps and websites, and keeps a simple history and notes file.

## Features

- Wake-word activation with configurable wake words.
- Direct commands for opening Google, YouTube, websites, and desktop apps.
- Voice search for Google and YouTube with confirmation before searching.
- Dictation into the active target, including WhatsApp Web support.
- Voice note taking and note playback.
- Audio testing and speech diagnostics.
- System actions such as shutdown and restart confirmation.
- Flask web dashboard with status, command history, note history, and settings controls.

## How It Works

1. `main.py` starts the assistant and keeps a continuous listen loop running.
2. The assistant listens for speech with the configured timeout values from `config.py`.
3. `nlp.py` maps phrases to intents such as `open_google`, `write_note`, or `search_youtube`.
4. `commands.py` executes the matched intent by speaking, opening apps, launching websites, dictating text, or saving notes.
5. `web_app.py` exposes a Flask dashboard so you can pause the assistant, review history, change wake words, and adjust speech settings.

## Project Structure

- `main.py` - main voice loop and wake-word handling.
- `commands.py` - command execution, dictation, app launching, and diagnostics.
- `nlp.py` - intent detection and phrase matching.
- `apps.py` - Windows app discovery and launch logic.
- `speech.py` - text-to-speech and microphone listening.
- `config.py` - persistent assistant settings.
- `memory.py` - note storage and retrieval.
- `history.py` - command history storage and retrieval.
- `web_app.py` - Flask dashboard and API endpoints.
- `test_assistant_features.py` - basic command and matching tests.
- `test_tts.py` - quick speech output test.

## Requirements

This project is intended for Windows because it uses `pywin32`, `comtypes`, and Windows app paths for some features.

Install the dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install the requirements.

```bash
pip install -r requirements.txt
```

3. Run the voice assistant.

```bash
python main.py
```

4. Optionally run the web dashboard.

```bash
python web_app.py
```

The dashboard runs at `http://127.0.0.1:5000` by default.

## Web API

- `GET /` - dashboard home page.
- `GET /api/status` - assistant status, latest command, and note count.
- `GET /api/history` - recent command and note history.
- `GET /api/notes` - recent notes only.
- `POST /toggle` - enable or pause the assistant.
- `POST /settings` - update wake words and speech/listening settings.

## Notes

- The assistant saves settings to `assistant_settings.json`.
- Notes are stored in `notes.txt`.
- Command history is stored in `command_history.txt`.
- If speech recognition or TTS does not work, check your microphone, Windows audio settings, and installed voice packages.