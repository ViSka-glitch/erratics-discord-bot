import discord
from discord.ext import commands
from discord import app_commands

import json
import os
import asyncio
import logging
import subprocess
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Import command handlers
from .commands.reload import reload_command
from .commands.sync import sync_command
from .commands.restart import restart_command
from .commands.dump_ids import dump_ids_command
from .commands.updatebot import updatebot_command
from .commands.utilities import listchannels_command

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def is_owner():
        """Decorator to ensure only the bot owner can use the command."""
        async def predicate(interaction: discord.Interaction) -> bool:
            return await interaction.client.is_owner(interaction.user)
        return app_commands.check(predicate)


    @app_commands.command(name="reload", description="Reload a specific cog module.")
    @is_owner()
    async def reload(self, interaction: discord.Interaction, cog: str):
        await reload_command(self, interaction, cog)

    @app_commands.command(name="sync", description="Manually sync all slash commands.")
    @is_owner()
    async def sync(self, interaction: discord.Interaction):
        await sync_command(self, interaction)

    @app_commands.command(name="restart", description="Restart the bot process (python3 bot.py).")
    @is_owner()
    async def restart(self, interaction: discord.Interaction):
        await restart_command(self, interaction)

    LOG_CHANNEL_ID = 1392804951553736717

    async def send_log_channel(self, message: str):
        channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        if channel:
            await channel.send(message)
        else:
            logging.warning(f"Log channel with ID {self.LOG_CHANNEL_ID} not found.")


    @app_commands.command(name="dump_ids", description="List all roles, channels, and categories with their IDs")
    @app_commands.checks.has_permissions(administrator=True)
    async def dump_ids(self, interaction: discord.Interaction):
        await dump_ids_command(self, interaction)

    @app_commands.command(name="listchannels", description="List all channels, categories, and roles with their names and IDs, grouped.")
    async def listchannels(self, interaction: discord.Interaction):
        await listchannels_command(self, interaction)


    @app_commands.command(name="updatebot", description="Run update_and_restart.sh and show the result (Owner only)")
    @is_owner()
    async def updatebot(self, interaction: discord.Interaction):
        await updatebot_command(self, interaction)

async def setup(bot: commands.Bot):
    await bot.add_cog(Developer(bot))
