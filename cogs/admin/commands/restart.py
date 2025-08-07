import discord
from discord import app_commands
import os

async def restart_command(self, interaction: discord.Interaction):
    await interaction.response.send_message("♻️ Restarting bot...", ephemeral=True)
    await self.bot.close()
    python_cmd = "python3 bot.py" if os.name != "nt" else "python bot.py"
    os.system(python_cmd)
