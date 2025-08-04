
# Erratics Discord Bot 🤖

![Python](https://img.shields.io/badge/python-3.12-blue) ![Discord.py](https://img.shields.io/badge/discord--py-2.5-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What is Erratics?

Erratics is a modular Discord bot written in Python (`discord.py`). It features a ticket system, verification workflow, moderation tools, logging, and more.

### Features

- **Verification Welcome Flow**
  - Private “✅ Verify” button on join
  - Public welcome message after verification
  - Auto-kick after 24h if not verified

- **Ticket System**
  - Live-updating ticket panel
  - Category selection, file upload support, close/archive/cancel
  - Persistent ticket logs and user tracking (see `tickets.json`)

- **Moderation & Utilities**
  - Slash commands, logging to file and channel, role management, Pomodoro timer, and more

### Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ViSka-glitch/erratics-discord-bot.git
   cd erratics-discord-bot
   ```

2. Create and fill your `.env` file:
   ```env
   DISCORD_TOKEN=your_token
   ```

3. Set up Python environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Start the bot:
   ```bash
   python3 bot.py
   ```

### Optional: Systemd Service

To run the bot as a service:
```bash
sudo cp example/discord-bot.service /etc/systemd/system/
sudo systemctl enable discord-bot
```

Use the update script:
```bash
bash update_and_restart.sh
```

### Data & Security

- `.env` is ignored by Git – keep tokens local
- Never commit private keys or tokens
- `join_pending.json` and `tickets.json` store temporary and persistent data
- All logs and errors are sent to a dedicated log channel and/or file

---

### Roadmap

- Add support for file uploads in tickets
- Multi-language welcome messages
- Rules acceptance checkbox before role assignment
- More modules (games, music, stats…)

---

## License

MIT License – see `LICENSE.md`.

---

## Contributing

Want to help? Please create issues for bug reports or feature requests, and submit PRs! We’ll review as soon as possible.
