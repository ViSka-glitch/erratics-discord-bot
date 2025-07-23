# Erratics Discord Bot 🤖

![Python](https://img.shields.io/badge/python-3.12-blue) ![Discord.py](https://img.shields.io/badge/discord--py-2.5-green)  
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🇩🇪 Beschreibung

Erratics ist ein modularer Discord-Bot mit Ticket‑System, Verifikations‑Workflow und mehr – in Python (`discord.py`) entwickelt.

### 🔧 Funktionen

- **Willkommensflow mit Verifizierung**  
  - Private Nachricht mit „✅ Verify“-Button beim Join  
  - Öffentliche Willkommensnachricht nach Klick  
  - Auto‑Kick bei Nicht‑Verifizierung nach 24 h

- **Ticket‑System**  
  - Automatisch aktualisierbares Ticket‑Panel  
  - Kategorien‑Auswahl, Upload‑Support, Schließen/Archivieren/Abbrechen etc.

- **Moderation & Utilities**  
  - Slash‑Commands, Logging, Rollen‑Verwaltung, Pomodoro, u.v.m.

### 🛠️ Installation & Setup

1. Repo klonen  
   ```bash
   git clone https://github.com/ViSka-glitch/erratics-discord-bot.git
   cd erratics-discord-bot
   ```

2. `.env` erstellen und ausfüllen  
   ```env
   DISCORD_TOKEN=dein_token
   ```

3. Python‑Umgebung & Installation  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Cogs laden:  
   - `welcomer.py` → Automatischer Verifikations‑Flow  
   - `tickets.py`, `mod.py` etc.

5. Bot starten  
   ```bash
   python3 bot.py
   ```

### ⚙️ Systemd (optional)

Wenn du den Bot als `discord-bot.service` betreibst:

```bash
sudo cp example/discord-bot.service /etc/systemd/system/
sudo systemctl enable discord-bot
```

Und mit dem Script:

```bash
bash update_and_restart.sh
```

### 🖥️ Daten & Token‑Sicherheit

- **`.env` bleibt lokal** – ist in `.gitignore`
- Private Keys und Tokens **niemals comitten**
- `join_pending.json` hält temporäre Daten – automatisch bereinigt

---

### 🚀 Roadmap

- 📎 Ticket‑System um Dateiuploads erweitern  
- 🇬🇧 Mehrsprachige Willkommensnachrichten  
- 📋 Regel‑Akzeptanz‑Checkbox vor Rollenvergabe  
- 🧩 Weitere Module (Games, Music, Stats…)

---

## 🇬🇧 English

### ❓ What is this?

Erratics is a modular Discord bot in Python (`discord.py`), featuring a ticket system, verification workflow, and more.

### 🛠️ Features

- **Verification welcome flow**  
  - Private “✅ Verify” button on join  
  - Public welcome message upon verification  
  - Auto‑kick after 24 h if unverified

- **Ticket System**  
  - Live‑updating ticket panel  
  - Category chooser, upload support, close/archive/cancel

- **Moderation & Utilities**  
  - Slash commands, logging, role management, Pomodoro, and more

### 📦 Installation

```bash
git clone https://github.com/ViSka-glitch/erratics-discord-bot.git
cd erratics-discord-bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```env
DISCORD_TOKEN=your_token
```

Then run:
```bash
python3 bot.py
```

### ⚙️ Optional Systemd Setup

Use the provided example service file:
```bash
sudo cp example/discord-bot.service /etc/systemd/system/
sudo systemctl enable discord-bot
```

Use `update_and_restart.sh` for updating & restarting.

### 🔐 Security

- `.env` is ignored by Git – keep tokens local.  
- `join_pending.json` auto-cleaned after 24 h.

### 📌 Roadmap

- Add support for file uploads in tickets  
- Multi‑language welcome messages  
- Rules acceptance checkbox before role assignment  
- More modules (games, music, stats…)

---

## 📝 License

MIT License – see `LICENSE.md`.

---

### 👋 Contributing

Want to help? Please create issues for bug reports or feature requests, and submit PRs! We’ll review asap.
