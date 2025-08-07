import discord
from discord.ext import commands
from discord import app_commands
import psutil
import time
import platform
import datetime
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Store the bot start time to calculate uptime
start_time = time.time()


# Modular command imports
from .commands.uptime import uptime_command
from .commands.shutdown import shutdown_command
from .commands.botstats import botstats_command

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="uptime", description="Show how long the bot has been running.")
    async def uptime(self, interaction: discord.Interaction):
        await uptime_command(self, interaction, start_time)

    @app_commands.command(name="shutdown", description="Shut down the bot (Owner only).")
    async def shutdown(self, interaction: discord.Interaction):
        await shutdown_command(self, interaction)

    @app_commands.command(name="botstats", description="Show memory, CPU and ping stats.")
    async def botstats(self, interaction: discord.Interaction):
        await botstats_command(self, interaction, self)

    async def _is_owner(self, interaction: discord.Interaction) -> bool:
        """Internal check to confirm if user is the bot owner."""
        return interaction.user.id == self.bot.owner_id

async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
