# --- bot.py ---
print("🟢 Bot is starting...")

import discord
import logging
# Logging-Konfiguration: Schreibe alle Logs in bot.log
logging.basicConfig(
    level=logging.INFO,
    filename="bot.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s"
)
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX", "!")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

owner_id_str = os.getenv("OWNER_ID")
if owner_id_str is None:
    raise ValueError("OWNER_ID is not set in the environment variables.")
bot.owner_id = int(owner_id_str)



# Modular slash command import
from cogs.bot.commands.status import status_command
from discord import app_commands

@bot.tree.command(name="status", description="Check if the bot is online.")
async def status(interaction: discord.Interaction):
    await status_command(interaction)

# --- Dynamischer Loader für alle Cogs & Events ---
async def load_all_extensions():
    cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
    events_dir = os.path.join(os.path.dirname(__file__), "events")
    extensions = []

    # Alle .py-Dateien in /cogs/ (rekursiv)
    for root, dirs, files in os.walk(cogs_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(root, os.path.dirname(__file__)).replace(os.sep, ".")
                module = f"{rel_path}.{file[:-3]}"
                extensions.append(module)

    # Alle .py-Dateien in /events/ (rekursiv)
    for root, dirs, files in os.walk(events_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(root, os.path.dirname(__file__)).replace(os.sep, ".")
                module = f"{rel_path}.{file[:-3]}"
                extensions.append(module)

    # Lade alle Extensions
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"🔄 Loaded: {ext}")
        except Exception as e:
            print(f"❌ Failed to load {ext}: {e}")

# --- Main ---
async def main():
    try:
        async with bot:
            await load_all_extensions()
            await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("🛑 Bot shutdown requested (KeyboardInterrupt).")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
