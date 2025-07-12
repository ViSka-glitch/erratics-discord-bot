# --- cogs/reactions.py ---
import discord
from discord.ext import commands
from datetime import datetime

class ReactionHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name != "✅":
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        default_role = discord.utils.get(guild.roles, name="🎖️ Member")
        if not default_role:
            default_role = await guild.create_role(name="🎖️ Member", colour=discord.Colour.blue())

        try:
            await member.add_roles(default_role)
            log_channel = discord.utils.get(guild.text_channels, name="🛰️│system-logs")
            if log_channel:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                await log_channel.send(f"✅ `{member.display_name}` has accepted the rules and received the 🎖️ Member role at `{timestamp}`")
        except Exception as e:
            print(f"Fehler beim Zuweisen der Rolle: {e}")

async def setup(bot):
    await bot.add_cog(ReactionHandler(bot))
