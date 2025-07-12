# --- events/on_ready.py ---
import discord
from discord.ext import commands
from datetime import datetime

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            bot_role = discord.utils.get(guild.roles, name="🤖 Bot")
            if not bot_role:
                bot_role = await guild.create_role(name="🤖 Bot", colour=discord.Colour.dark_grey())

            bot_member = guild.get_member(self.bot.user.id)
            if bot_member and bot_role not in bot_member.roles:
                await bot_member.add_roles(bot_role)

            log_channel = discord.utils.get(guild.text_channels, name="🔒│classified-logs")
            if log_channel:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                await log_channel.send(f"🤖 Bot ist online und Rolle wurde gesetzt (`{guild.name}` at `{timestamp}`)")

        print(f"{self.bot.user} ist online.")

async def setup(bot):
    await bot.add_cog(OnReady(bot))
