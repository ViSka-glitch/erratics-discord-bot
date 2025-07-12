# --- events/on_channel.py ---
import discord
from discord.ext import commands

class OnChannelCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not isinstance(channel.guild, discord.Guild):
            return

        bot_role = discord.utils.get(channel.guild.roles, name="🤖 Bot")
        if not bot_role:
            return

        perms = None
        if isinstance(channel, discord.TextChannel):
            perms = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_messages=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                use_application_commands=True
            )
        elif isinstance(channel, discord.VoiceChannel):
            perms = discord.PermissionOverwrite(
                connect=True,
                speak=True,
                use_voice_activation=True
            )

        if perms:
            await channel.set_permissions(bot_role, overwrite=perms)

async def setup(bot):
    await bot.add_cog(OnChannelCreate(bot))
