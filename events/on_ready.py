import discord
from discord.ext import commands
from datetime import datetime

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            # Rolle erstellen, falls nicht vorhanden
            bot_role = discord.utils.get(guild.roles, name="🤖 Bot")
            if not bot_role:
                bot_role = await guild.create_role(name="🤖 Bot", colour=discord.Colour.dark_grey())

            # Rolle dem Bot zuweisen
            bot_member = guild.get_member(self.bot.user.id)
            if bot_member and bot_role not in bot_member.roles:
                await bot_member.add_roles(bot_role)

            # Log-Kanal finden und melden
            log_channel = discord.utils.get(guild.text_channels, name="🔒│classified-logs")
            if log_channel:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                await log_channel.send(
                    f"🤖 Bot ist online und Rolle wurde gesetzt (`{guild.name}` at `{timestamp}`)")

        # Slash-Commands synchronisieren
        try:
            synced = await self.bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash command(s).")
        except Exception as e:
            print(f"❌ Slash command sync failed: {e}")

        print(f"{self.bot.user} ist online.")

async def setup(bot):
    await bot.add_cog(OnReady(bot))
