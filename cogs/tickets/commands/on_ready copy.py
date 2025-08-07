import discord
from discord.ext import commands
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

from cogs.tickets.tickets import TicketCreateView, load_ticket_data  # 💡 Dateiname angepasst
from config.ids import LOG_CHANNEL_ID

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            # Bot-Rolle erstellen, falls nicht vorhanden
            bot_role = discord.utils.get(guild.roles, name="🤖 Bot")
            if not bot_role:
                bot_role = await guild.create_role(name="🤖 Bot", colour=discord.Colour.dark_grey())

            # Bot-Rolle zuweisen
            bot_member = guild.get_member(self.bot.user.id)
            if bot_member and bot_role not in bot_member.roles:
                await bot_member.add_roles(bot_role)

            # Log senden
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                await log_channel.send(
                    f"🤖 Bot is online and role was assigned (`{guild.name}` at `{timestamp}`)"
                )

        # Persistent Views für Buttons registrieren
        try:
            ticket_data = load_ticket_data()
            active_tickets = ticket_data.get("active_tickets", {})

            self.bot.add_view(TicketCreateView(self.bot, active_tickets))
            logging.info("✅ Persistent views registered.")
        except Exception as e:
            logging.error(f"❌ Failed to register views: {e}")

        # Slash-Commands synchronisieren
        try:
            synced = await self.bot.tree.sync()
            logging.info(f"✅ Synced {len(synced)} slash command(s).")
        except Exception as e:
            logging.error(f"❌ Slash command sync failed: {e}")

        print(f"{self.bot.user} is online.")
        logging.info(f"{self.bot.user} is online.")

async def setup(bot: commands.Bot):
    if bot.get_cog("OnReady") is None:
        await bot.add_cog(OnReady(bot))
    else:
        logging.warning("⚠️ OnReady already registered – skipping.")
