
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import qrcode
from io import BytesIO
import platform
import psutil

# Modular command imports
from .commands.ping import ping_command
from .commands.botinfo import botinfo_command
from .commands.helpbot import helpbot_command
from .commands.serverinvite import serverinvite_command
from .commands.infobot import infobot_command

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Replies with Pong!")
    async def ping(self, interaction: discord.Interaction):
        await ping_command(self, interaction)

    @app_commands.command(name="botinfo", description="Show basic information about the bot.")
    async def botinfo(self, interaction: discord.Interaction):
        await botinfo_command(self, interaction)

    @app_commands.command(name="helpbot", description="Show a help message with all basic commands.")
    async def helpbot(self, interaction: discord.Interaction):
        await helpbot_command(self, interaction)

    @app_commands.command(name="serverinvite", description="Generate a permanent invite link and QR code.")
    async def serverinvite(self, interaction: discord.Interaction):
        await serverinvite_command(self, interaction)

    @app_commands.command(name="infobot", description="Show information about this bot.")
    async def infobot(self, interaction: discord.Interaction):
        await infobot_command(self, interaction)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
