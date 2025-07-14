import discord
from discord.ext import commands

# Constants
MEMBER_ROLE_ID = 1392804906804707369       # 🎖️ Member role
LOG_CHANNEL_ID = 1392804915516149880       # 🛰️│system-logs
TARGET_EMOJI = "✅"

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Assigns the Member role when someone reacts with ✅."""
        if payload.emoji.name != TARGET_EMOJI:
            return  # Ignore other reactions

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        role = guild.get_role(MEMBER_ROLE_ID)
        if not role:
            return

        try:
            await member.add_roles(role, reason="Reaction role via ✅")
        except discord.Forbidden:
            return  # Missing permissions
        except Exception as e:
            print(f"Error assigning role: {e}")
            return

        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"✅ `{member}` received the role `{role.name}` via reaction.")

async def setup(bot):
    await bot.add_cog(Reactions(bot))
