import discord
from discord.ext import commands, tasks
import logging
import asyncio
import json
import os
from dotenv import load_dotenv
from .remote_client import SpaceEngineersRemoteClient
from .commands.se_status import se_status_command

load_dotenv()
SE_REMOTE_URI = os.getenv("SE_REMOTE_URI", "ws://127.0.0.1:8080/")
SE_REMOTE_KEY = os.getenv("SE_REMOTE_KEY")

class SpaceEngineersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.se_client = SpaceEngineersRemoteClient(SE_REMOTE_URI, SE_REMOTE_KEY)
        self.status = None
        self.bg_task = self.bot.loop.create_task(self.se_connect_loop())

    async def cog_unload(self):
        # Beende Hintergrundtask und schließe die Session sauber
        if hasattr(self, 'bg_task') and self.bg_task:
            self.bg_task.cancel()
            try:
                await self.bg_task
            except asyncio.CancelledError:
                pass
        await self.se_client.disconnect()

    async def se_connect_loop(self):
        while True:
            if not self.se_client.connected:
                # Vorherige Session schließen, falls noch offen
                await self.se_client.disconnect()
                await self.se_client.connect()
            await asyncio.sleep(10)

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("[SE-Remote] Space Engineers Cog ready.")

    @discord.app_commands.command(name="se_status", description="Get Space Engineers server status.")
    async def se_status(self, interaction: discord.Interaction):
        await se_status_command(self, interaction)

async def setup(bot: commands.Bot):
    await bot.add_cog(SpaceEngineersCog(bot))
