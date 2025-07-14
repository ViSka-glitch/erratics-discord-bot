import discord
from discord.ext import commands
from discord import app_commands
import io

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

        await interaction.response.send_message(
            content="📄 Here is the list of all channel names and their IDs:",
            file=file,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Utilities(bot))
