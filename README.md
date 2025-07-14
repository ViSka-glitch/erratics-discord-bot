# 🤖 Erratics Discord Bot

**Unpredictable. Powerful. Built for gamers.**  
A modular and scalable Discord bot built for the **Erratics** community – focused on automation, moderation, ticketing and member onboarding.

---

## 🚀 Core Features

| Module            | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| 👋 Welcome         | Interactive onboarding with confirmation button                            |
| 🎫 Ticketing       | Channel-based ticket system with panel, log, and transcript support         |
| 🛡️ Moderation      | Slash-based moderation: kick, ban, timeout, unban, clear, logging           |
| 💬 Info & Utility  | Uptime, bot/system stats, help, restart, version checks                    |
| 🧬 Quickstart      | Guides and links via `🧬│initiate-sequence`                                 |
| 📦 Auto Layout     | Slash command to auto-generate categories and channels                      |
| ✅ Role Assignment | Reaction-based role onboarding via ✅ confirmation                           |

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/ViSka-glitch/erratics-discord-bot.git
cd erratics-discord-bot

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory with:

```env
TOKEN=your-bot-token-here
PREFIX=!
```

- `TOKEN`: your Discord bot token
- `PREFIX`: legacy fallback, default is `!` (used for some internal functions)

---

## 🧪 Running the Bot

```bash
python3 bot.py
```

---

## 📡 Slash Commands

### 🎫 Ticketing
- `/setticketpanel` – Creates the panel with "Open Ticket" button
- Auto-closes and logs tickets into `🔒-ticket-logs`

### 🛡️ Moderation
- `/kick @user reason`
- `/ban @user reason`
- `/unban user_id`
- `/timeout @user minutes reason`
- `/clear amount` – Bulk message delete
- ➕ All actions logged in `🛡│mod-log`

### 💬 Info / Tools
- `/ping` – Responds with `Pong!`
- `/uptime` – Shows how long the bot is running
- `/botinfo` – Bot prefix, status
- `/infobot` – System info, CPU, RAM, latency
- `/helpbot` – Sends help via DM

### 🧑‍💻 Developer
- `/reload cogname`
- `/sync` – Force sync slash commands
- `/restart` – Restarts bot via `python3 bot.py` (owner only)

---

## 🧱 Project Structure

```bash
.
├── bot.py                    # Bot entry point
├── .env                      # Environment config
├── requirements.txt          # Python dependencies
├── /cogs                     # Modular command/event folders
│   ├── basic.py
│   ├── developer.py
│   ├── info.py
│   ├── layout.py
│   ├── mod.py
│   ├── reactions.py
│   ├── tickets.py
│   ├── welcomer.py
│   └── system.py
├── /events
│   └── on_ready.py
```

---

## 🔁 Updating via Git & VM

```bash
# On development system
git add .
git commit -m "Your message"
git push

# On production VM
cd /home/botuser/discord-bot/
git pull origin main
python3 bot.py
```

---

## 📜 License

This project is private and licensed to the Erratics community.  
Contact [ViSka-glitch](https://github.com/ViSka-glitch) for collaboration.
