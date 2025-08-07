import discord
from discord.ext import commands
from discord import app_commands
import io
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
LOG_CHANNEL_ID = 1392804951553736717

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="listchannels", description="List all channels, categories, and roles with their names and IDs, grouped.")
    async def listchannels(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        guild = interaction.guild
        output = []

        # Categories
        output.append("# Categories:")
        for category in guild.categories:
            output.append(f"{category.name} – `{category.id}` (Category)")

        # Text Channels
        output.append("\n# Text Channels:")
        for channel in guild.text_channels:
            output.append(f"{channel.name} – `{channel.id}` (Text)")

        # Voice Channels
        output.append("\n# Voice Channels:")
        for channel in guild.voice_channels:
            output.append(f"{channel.name} – `{channel.id}` (Voice)")

        # Other Channels
        others = [c for c in guild.channels if c not in guild.text_channels and c not in guild.voice_channels and c not in guild.categories]
        if others:
            output.append("\n# Other Channels:")
            for channel in others:
                type_name = str(channel.type).replace("ChannelType.", "")
                output.append(f"{channel.name} – `{channel.id}` ({type_name})")

        # Roles
        output.append("\n# Roles:")
        for role in guild.roles:
            if role.is_default():
                continue
            output.append(f"{role.name} – `{role.id}`")

        content = "\n".join(output)
        buffer = io.BytesIO(content.encode("utf-8"))
        file = discord.File(fp=buffer, filename="server_overview.txt")

        try:
            await interaction.response.send_message(
                content="📄 Here is the grouped list of all categories, channels, and roles:",
                file=file,
                ephemeral=True
            )
            log_msg = f"✅ Server overview sent by {interaction.user} ({interaction.user.id}) in guild '{guild.name}' ({guild.id})."
            logging.info(log_msg)
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(log_msg)
        except Exception as e:
            error_msg = f"❌ Error sending server overview by {interaction.user} ({interaction.user.id}) in guild '{guild.name}' ({guild.id}): {e}"
            logging.error(error_msg)
            await interaction.response.send_message(f"❌ Error sending server overview: {e}", ephemeral=True)
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(error_msg)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utilities(bot))
