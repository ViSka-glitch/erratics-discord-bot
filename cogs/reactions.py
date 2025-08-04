import discord
from discord.ext import commands
from config.ids import VERIFY_ID, LOG_CHANNEL_ID
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Constants
TARGET_EMOJI = "✅"

class Reactions(commands.Cog):
    async def log_action(self, guild, message):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(message)
        else:
            logging.warning(f"Log-Channel mit ID {LOG_CHANNEL_ID} nicht gefunden.")
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Assigns the Member role when someone reacts with ✅."""
        if payload.emoji.name != TARGET_EMOJI:
            return  # Ignore other reactions

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            logging.warning(f"Guild mit ID {payload.guild_id} nicht gefunden.")
            return

        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            logging.info(f"User {payload.user_id} ist kein Member oder ein Bot.")
            return

        role = guild.get_role(VERIFY_ID)
        if not role:
            await self.log_action(guild, f"❌ Verify-Rolle mit ID {VERIFY_ID} nicht gefunden.")
            return

        try:
            await member.add_roles(role, reason="Reaction role via ✅")
        except discord.Forbidden:
            await self.log_action(guild, f"❌ Missing permissions to assign role `{role.name}` to `{member}`.")
            return
        except Exception as e:
            await self.log_action(guild, f"❌ Error assigning role: {e}")
            logging.error(f"Error assigning role: {e}")
            return

        await self.log_action(guild, f"✅ `{member}` received the role `{role.name}` via reaction.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name != TARGET_EMOJI:
            return  # Ignore other reactions

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            logging.warning(f"Guild mit ID {payload.guild_id} nicht gefunden.")
            return

        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            logging.info(f"User {payload.user_id} ist kein Member oder ein Bot.")
            return

        role = guild.get_role(VERIFY_ID)
        if not role:
            await self.log_action(guild, f"❌ Verify-Rolle mit ID {VERIFY_ID} nicht gefunden.")
            return

        try:
            await member.remove_roles(role, reason="Reaction role removed via ✅")
        except discord.Forbidden:
            await self.log_action(guild, f"❌ Missing permissions to remove role `{role.name}` from `{member}`.")
            return
        except Exception as e:
            await self.log_action(guild, f"❌ Error removing role: {e}")
            logging.error(f"Error removing role: {e}")
            return

        await self.log_action(guild, f"❎ `{member}` lost the role `{role.name}` by removing reaction.")

async def setup(bot):
    await bot.add_cog(Reactions(bot))
