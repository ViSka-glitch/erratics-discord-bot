import discord
from discord.ext import commands

BOT_ROLE_ID = 1392804905353347163  # 🤖 Bot role ID

class OnChannelCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Automatically assigns permissions to the 🤖 Bot role when a new channel is created."""
        if not isinstance(channel.guild, discord.Guild):
            return

        bot_role = channel.guild.get_role(BOT_ROLE_ID)
        if not bot_role:
            return

        # Define permissions based on channel type
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

        # Apply permissions if valid
        if perms:
            await channel.set_permissions(bot_role, overwrite=perms)

async def setup(bot):
    await bot.add_cog(OnChannelCreate(bot))
