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

    @app_commands.command(name="listchannels", description="List all channels with their names and IDs.")
    async def listchannels(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        guild = interaction.guild
        output = []

        for channel in guild.channels:
            type_name = str(channel.type).replace("ChannelType.", "")
            output.append(f"{channel.name} – `{channel.id}` ({type_name})")

        content = "\n".join(output)
        buffer = io.BytesIO(content.encode("utf-8"))
        file = discord.File(fp=buffer, filename="channel_list.txt")

        try:
            await interaction.response.send_message(
                content="📄 Here is the list of all channel names and their IDs:",
                file=file,
                ephemeral=True
            )
            log_msg = f"✅ Channel list sent by {interaction.user} ({interaction.user.id}) in guild '{guild.name}' ({guild.id})."
            logging.info(log_msg)
            # Sende Log-Meldung in Log-Channel
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(log_msg)
        except Exception as e:
            error_msg = f"❌ Error sending channel list by {interaction.user} ({interaction.user.id}) in guild '{guild.name}' ({guild.id}): {e}"
            logging.error(error_msg)
            await interaction.response.send_message(f"❌ Error sending channel list: {e}", ephemeral=True)
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(error_msg)

async def setup(bot):
    await bot.add_cog(Utilities(bot))
