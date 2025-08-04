import discord
from discord.ext import commands
from config.ids import VERIFY_ID, LOG_CHANNEL_ID
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Constants
TARGET_EMOJI = "✅"

# Emoji zu Rollen-Mapping
ROLE_EMOJI_MAP = {
    "✅": VERIFY_ID,  # Verifizierung
    "🧟": 1402000607207886928,  # 7 Days Outpost
    "🏹": 1401999743898357952,  # Valheim Nexus
    "🚀": 1402000758697889963   # SE Cluster
}

class Reactions(commands.Cog):
    async def log_action(self, guild, message):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(message)
        else:
            logging.warning(f"Log-Channel mit ID {LOG_CHANNEL_ID} nicht gefunden.")
    @commands.command(name="post_reaction_roles")
    @commands.has_permissions(administrator=True)
    async def post_reaction_roles(self, ctx):
        """Postet ein Embed mit den Reaction-Rollen im Channel-Unlocker und fügt die Emojis hinzu."""
        channel_unlocker_id = 1392804917378416732
        channel = ctx.guild.get_channel(channel_unlocker_id)
        if not channel:
            await ctx.send(f"❌ Channel-Unlocker mit ID {channel_unlocker_id} nicht gefunden.")
            return
        embed = discord.Embed(title="Channel Unlocker: Game Roles",
                              description="React with the matching emoji to unlock access to the game categories!",
                              color=discord.Color.blue())
        embed.add_field(name="🧟 7 Days Outpost", value="Unlock access to 7 Days to Die", inline=False)
        embed.add_field(name="🏹 Valheim Nexus", value="Unlock access to Valheim", inline=False)
        embed.add_field(name="🚀 SE Cluster", value="Unlock access to Space Engineers", inline=False)
        msg = await channel.send(embed=embed)
        # Emojis hinzufügen
        for emoji in ["🧟", "🏹", "🚀"]:
            await msg.add_reaction(emoji)
        await ctx.send(f"✅ Reaction-Rollen Nachricht im Channel-Unlocker gepostet.")
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            logging.warning(f"Guild mit ID {payload.guild_id} nicht gefunden.")
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            logging.info(f"User {payload.user_id} ist kein Member oder ein Bot.")
            return
        role_id = ROLE_EMOJI_MAP.get(payload.emoji.name)
        if not role_id:
            return  # Ignore other reactions
        role = guild.get_role(role_id)
        if not role:
            await self.log_action(guild, f"❌ Rolle mit ID {role_id} nicht gefunden für Emoji {payload.emoji.name}.")
            return
        try:
            await member.add_roles(role, reason=f"Reaction role via {payload.emoji.name}")
        except discord.Forbidden:
            await self.log_action(guild, f"❌ Missing permissions to assign role `{role.name}` to `{member}`.")
            return
        except Exception as e:
            await self.log_action(guild, f"❌ Error assigning role: {e}")
            logging.error(f"Error assigning role: {e}")
            return
        await self.log_action(guild, f"✅ `{member}` received the role `{role.name}` via reaction {payload.emoji.name}.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            logging.warning(f"Guild mit ID {payload.guild_id} nicht gefunden.")
            return
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            logging.info(f"User {payload.user_id} ist kein Member oder ein Bot.")
            return
        role_id = ROLE_EMOJI_MAP.get(payload.emoji.name)
        if not role_id:
            return  # Ignore other reactions
        role = guild.get_role(role_id)
        if not role:
            await self.log_action(guild, f"❌ Rolle mit ID {role_id} nicht gefunden für Emoji {payload.emoji.name}.")
            return
        try:
            await member.remove_roles(role, reason=f"Reaction role removed via {payload.emoji.name}")
        except discord.Forbidden:
            await self.log_action(guild, f"❌ Missing permissions to remove role `{role.name}` from `{member}`.")
            return
        except Exception as e:
            await self.log_action(guild, f"❌ Error removing role: {e}")
            logging.error(f"Error removing role: {e}")
            return
        await self.log_action(guild, f"❎ `{member}` lost the role `{role.name}` by removing reaction {payload.emoji.name}.")

async def setup(bot):
    await bot.add_cog(Reactions(bot))
