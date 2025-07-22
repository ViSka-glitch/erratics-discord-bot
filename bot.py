# --- bot.py ---
import discord
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
bot.owner_id = int(os.getenv("OWNER_ID"))


# --- Event: Bot gestartet ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")

# --- Befehl: Status prüfen ---
@bot.command()
async def status(ctx):
    await ctx.send(f"✅ I'm online! {bot.user} is running.")

# --- Erweiterungen laden ---
async def load_extensions():
    extensions = [
        "cogs.basic",
        "cogs.welcomer",
        "cogs.layout",
        "cogs.mod",
        "cogs.utilities",
        "cogs.tickets",
        "cogs.info",
        "cogs.system",
        "cogs.developer",
        "cogs.reactions",
        "events.on_ready",
        "events.on_channel"
    ]
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
            await load_extensions()
            await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("🛑 Bot shutdown requested (KeyboardInterrupt).")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
