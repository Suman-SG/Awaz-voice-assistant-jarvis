from flask import Flask, jsonify, redirect, render_template_string, request, url_for

from config import load_settings, save_settings
from history import read_command_history
from memory import read_notes


app = Flask(__name__)


PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Awaz</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #0f172a;
      --panel: rgba(15, 23, 42, 0.88);
      --card: rgba(255, 255, 255, 0.08);
      --card-border: rgba(255, 255, 255, 0.12);
      --text: #e5eefc;
      --muted: #9fb1d1;
      --accent: #38bdf8;
      --accent-strong: #0ea5e9;
      --success: #22c55e;
      --danger: #f97316;
      --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
      --radius: 22px;
      --user: #f97316;
      --jarvis: #38bdf8;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", "Arial", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.26), transparent 28%),
        radial-gradient(circle at top right, rgba(34, 197, 94, 0.18), transparent 24%),
        linear-gradient(160deg, #020617 0%, #0f172a 42%, #111827 100%);
    }

    .shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 18px 44px;
    }

    .hero {
      display: grid;
      gap: 18px;
      grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.8fr);
      align-items: stretch;
      margin-bottom: 22px;
    }

    .hero-card,
    .panel {
      border: 1px solid var(--card-border);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.04));
      backdrop-filter: blur(14px);
      box-shadow: var(--shadow);
      border-radius: var(--radius);
    }

    .hero-card {
      padding: 26px;
      position: relative;
      overflow: hidden;
    }

    .hero-topline {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
    }

    .hero-card::after {
      content: "";
      position: absolute;
      inset: auto -16% -35% auto;
      width: 280px;
      height: 280px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(56, 189, 248, 0.32), transparent 68%);
      pointer-events: none;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(56, 189, 248, 0.12);
      color: #8ddcff;
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 700;
    }

    .live-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 12px;
      border-radius: 999px;
      background: rgba(34, 197, 94, 0.12);
      color: #86efac;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }

    .live-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.45);
      animation: pulse 1.7s infinite;
    }

    h1, h2, h3, p { margin: 0; }

    h1 {
      margin-top: 14px;
      font-size: clamp(2rem, 4vw, 3.8rem);
      line-height: 1.02;
      max-width: 10ch;
    }

    .lede {
      margin-top: 14px;
      max-width: 60ch;
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.7;
    }

    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 20px;
    }

    .wave-wrap {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 24px;
      padding: 16px 18px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.08);
      width: fit-content;
    }

    .wave-bar {
      width: 7px;
      border-radius: 999px;
      background: linear-gradient(180deg, #8ddcff, #0ea5e9);
      animation: wave 1.2s ease-in-out infinite;
      transform-origin: center bottom;
    }

    .wave-bar:nth-child(1) { height: 14px; animation-delay: 0.0s; }
    .wave-bar:nth-child(2) { height: 28px; animation-delay: 0.12s; }
    .wave-bar:nth-child(3) { height: 18px; animation-delay: 0.24s; }
    .wave-bar:nth-child(4) { height: 34px; animation-delay: 0.36s; }
    .wave-bar:nth-child(5) { height: 20px; animation-delay: 0.48s; }
    .wave-bar:nth-child(6) { height: 30px; animation-delay: 0.6s; }
    .wave-bar:nth-child(7) { height: 16px; animation-delay: 0.72s; }

    .wave-label {
      margin-left: 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    .button {
      appearance: none;
      border: none;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      min-height: 46px;
      padding: 0 16px;
      border-radius: 14px;
      font-weight: 700;
      transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
    }

    .button:hover { transform: translateY(-1px); }

    .button.primary {
      background: linear-gradient(135deg, var(--accent), var(--accent-strong));
      color: #001018;
      box-shadow: 0 16px 36px rgba(14, 165, 233, 0.28);
    }

    .button.secondary {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stat-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .stat {
      padding: 18px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.08);
      min-height: 110px;
    }

    .stat .label {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    .stat .value {
      margin-top: 10px;
      font-size: 1.5rem;
      font-weight: 800;
      word-break: break-word;
    }

    .status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-top: 10px;
      padding: 7px 10px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
    }

    .status.on { background: rgba(34, 197, 94, 0.16); color: #86efac; }
    .status.off { background: rgba(249, 115, 22, 0.16); color: #fdba74; }

    .panel-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    .chat-grid {
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin-top: 18px;
    }

    .chat-column {
      display: grid;
      gap: 12px;
    }

    .chat-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 6px;
    }

    .chat-title span {
      color: var(--muted);
      font-size: 13px;
    }

    .chat-column.jarvis .item {
      border-left: 4px solid var(--jarvis);
    }

    .chat-column.user .item {
      border-left: 4px solid var(--user);
    }

    .chat-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }

    .chat-badge.jarvis {
      background: rgba(56, 189, 248, 0.14);
      color: #8ddcff;
    }

    .chat-badge.user {
      background: rgba(249, 115, 22, 0.14);
      color: #fdba74;
    }

    .panel {
      padding: 20px;
    }

    .panel h2 {
      font-size: 1.15rem;
      margin-bottom: 14px;
    }

    .scroll-list {
      display: grid;
      gap: 10px;
      max-height: 380px;
      overflow: auto;
      padding-right: 4px;
    }

    .item {
      padding: 14px 15px;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      line-height: 1.55;
      color: #dbe7fb;
    }

    .item small {
      display: block;
      color: var(--muted);
      margin-bottom: 6px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .form-grid {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .field {
      display: grid;
      gap: 7px;
    }

    label {
      font-size: 13px;
      color: var(--muted);
    }

    input[type="text"],
    input[type="number"],
    input[type="range"] {
      width: 100%;
    }

    input[type="text"],
    input[type="number"] {
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(2, 6, 23, 0.75);
      color: var(--text);
      outline: none;
    }

    .range-wrap {
      display: grid;
      gap: 8px;
    }

    .range-value {
      color: #8ddcff;
      font-weight: 700;
      font-size: 13px;
    }

    .footer-note {
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
    }

    @keyframes wave {
      0%, 100% { transform: scaleY(0.55); opacity: 0.72; }
      50% { transform: scaleY(1.25); opacity: 1; }
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.45); }
      70% { box-shadow: 0 0 0 14px rgba(34, 197, 94, 0); }
      100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    @media (max-width: 920px) {
      .hero,
      .panel-grid,
      .form-grid,
      .chat-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-card">
        <div class="hero-topline">
          <span class="eyebrow">Awaz / voice control center</span>
          <span class="live-pill"><span class="live-dot"></span> Jarvis online{% if settings['ASSISTANT_ENABLED'] %} and listening{% else %} and paused{% endif %}</span>
        </div>
        <h1>Two-way voice cockpit for Jarvis and you.</h1>
        <p class="lede">Track what Jarvis heard, what it answered, and keep the voice assistant tuned from a single polished panel.</p>
        <div class="hero-actions">
          <form method="post" action="{{ url_for('toggle_assistant') }}">
            <button class="button primary" type="submit">{{ 'Stop assistant' if settings['ASSISTANT_ENABLED'] else 'Start assistant' }}</button>
          </form>
          <a class="button secondary" href="{{ url_for('index') }}">Refresh panel</a>
        </div>
        <div class="wave-wrap" aria-label="Speaking indicator">
          <span class="wave-bar"></span>
          <span class="wave-bar"></span>
          <span class="wave-bar"></span>
          <span class="wave-bar"></span>
          <span class="wave-bar"></span>
          <span class="wave-bar"></span>
          <span class="wave-bar"></span>
          <span class="wave-label">Live voice wave</span>
        </div>
      </div>

      <div class="panel">
        <div class="stat-grid">
          <div class="stat">
            <div class="label">Assistant state</div>
            <div class="value">{{ 'Running' if settings['ASSISTANT_ENABLED'] else 'Paused' }}</div>
            <div class="status {{ 'on' if settings['ASSISTANT_ENABLED'] else 'off' }}">{{ 'Enabled' if settings['ASSISTANT_ENABLED'] else 'Disabled' }}</div>
          </div>
          <div class="stat">
            <div class="label">Wake words</div>
            <div class="value">{{ settings['WAKE_WORDS'] | join(', ') }}</div>
          </div>
          <div class="stat">
            <div class="label">Confidence threshold</div>
            <div class="value">{{ settings['MATCH_THRESHOLD'] }}</div>
          </div>
          <div class="stat">
            <div class="label">Speech rate</div>
            <div class="value">{{ settings['SPEECH_RATE'] }}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="chat-grid">
      <div class="panel chat-column jarvis">
        <div class="chat-title">
          <h2>Jarvis messages</h2>
          <span>Assistant side</span>
        </div>
        <div class="scroll-list">
          {% for command in command_history %}
            <div class="item"><small>Jarvis</small>{{ command }}</div>
          {% else %}
            <div class="item"><small>Jarvis</small>No assistant messages yet.</div>
          {% endfor %}
        </div>
      </div>

      <div class="panel chat-column user">
        <div class="chat-title">
          <h2>Your voice messages</h2>
          <span>User side</span>
        </div>
        <div class="scroll-list">
          {% for note in notes %}
            <div class="item"><small>You</small>{{ note }}</div>
          {% else %}
            <div class="item"><small>You</small>No voice notes yet.</div>
          {% endfor %}
        </div>
      </div>
    </section>

    <section class="panel" style="margin-bottom: 18px;">
      <h2>Settings</h2>
      <form method="post" action="{{ url_for('update_settings') }}">
        <div class="form-grid">
          <div class="field">
            <label for="wake_words">Wake words, comma separated</label>
            <input id="wake_words" name="wake_words" type="text" value="{{ settings['WAKE_WORDS'] | join(', ') }}">
          </div>
          <div class="field">
            <label for="match_threshold">Confidence threshold</label>
            <input id="match_threshold" name="match_threshold" type="number" min="0" max="100" value="{{ settings['MATCH_THRESHOLD'] }}">
          </div>
          <div class="field range-wrap">
            <label for="speech_rate">Speech rate</label>
            <input id="speech_rate" name="speech_rate" type="range" min="100" max="240" value="{{ settings['SPEECH_RATE'] }}" oninput="speechRateValue.textContent = this.value">
            <div class="range-value">Current: <span id="speechRateValue">{{ settings['SPEECH_RATE'] }}</span></div>
          </div>
          <div class="field range-wrap">
            <label for="speech_volume">Speech volume</label>
            <input id="speech_volume" name="speech_volume" type="range" min="0" max="1" step="0.05" value="{{ settings['SPEECH_VOLUME'] }}" oninput="speechVolumeValue.textContent = this.value">
            <div class="range-value">Current: <span id="speechVolumeValue">{{ settings['SPEECH_VOLUME'] }}</span></div>
          </div>
          <div class="field">
            <label for="listen_timeout">Listen timeout</label>
            <input id="listen_timeout" name="listen_timeout" type="number" min="1" max="30" value="{{ settings['LISTEN_TIMEOUT'] }}">
          </div>
          <div class="field">
            <label for="command_timeout">Command timeout</label>
            <input id="command_timeout" name="command_timeout" type="number" min="1" max="30" value="{{ settings['COMMAND_TIMEOUT'] }}">
          </div>
        </div>
        <div class="hero-actions" style="margin-top: 16px;">
          <button class="button primary" type="submit">Save settings</button>
        </div>
      </form>
      <div class="footer-note">Settings are saved to the shared assistant config file and are applied the next time the voice loop reads them.</div>
    </section>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    settings = load_settings()
    command_history = read_command_history(limit=25)
    notes = read_notes()[-25:]
    return render_template_string(
        PAGE_TEMPLATE,
        settings=settings,
        command_history=command_history,
        notes=notes,
    )


@app.route("/api/status")
def api_status():
    settings = load_settings()
    command_history = read_command_history(limit=1)
    notes = read_notes()

    return jsonify({
        "assistant_enabled": settings.get("ASSISTANT_ENABLED", True),
        "wake_words": settings.get("WAKE_WORDS", []),
        "match_threshold": settings.get("MATCH_THRESHOLD", 50),
        "speech_rate": settings.get("SPEECH_RATE", 170),
        "latest_command": command_history[-1] if command_history else None,
        "command_count": len(read_command_history(limit=1000)),
        "note_count": len(notes),
        "last_note": notes[-1] if notes else None,
    })


@app.route("/api/history")
def api_history():
    return jsonify({
        "commands": read_command_history(limit=50),
        "notes": read_notes()[-50:],
    })


@app.route("/api/notes")
def api_notes():
    return jsonify({
        "notes": read_notes()[-50:],
    })


@app.route("/toggle", methods=["POST"])
def toggle_assistant():
    settings = load_settings()
    settings["ASSISTANT_ENABLED"] = not settings.get("ASSISTANT_ENABLED", True)
    save_settings(settings)
    return redirect(url_for("index"))


@app.route("/settings", methods=["POST"])
def update_settings():
    settings = load_settings()
    wake_words = request.form.get("wake_words", "")

    settings.update({
        "WAKE_WORDS": [word.strip().lower() for word in wake_words.split(",") if word.strip()],
        "MATCH_THRESHOLD": int(request.form.get("match_threshold", settings["MATCH_THRESHOLD"])),
        "SPEECH_RATE": int(request.form.get("speech_rate", settings["SPEECH_RATE"])),
        "SPEECH_VOLUME": float(request.form.get("speech_volume", settings["SPEECH_VOLUME"])),
        "LISTEN_TIMEOUT": int(request.form.get("listen_timeout", settings["LISTEN_TIMEOUT"])),
        "COMMAND_TIMEOUT": int(request.form.get("command_timeout", settings["COMMAND_TIMEOUT"])),
    })

    save_settings(settings)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
