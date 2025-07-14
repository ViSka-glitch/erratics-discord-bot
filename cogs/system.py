import discord
from discord.ext import commands
from discord import app_commands
import psutil
import time
import platform
import datetime

# Store the bot start time to calculate uptime
start_time = time.time()

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="uptime", description="Show how long the bot has been running.")
    async def uptime(self, interaction: discord.Interaction):
        """Returns the bot's uptime in HH:MM:SS format."""
        current_time = time.time()
        uptime_seconds = int(current_time - start_time)
        uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
        await interaction.response.send_message(f"🕒 Uptime: `{uptime_str}`")

    @app_commands.command(name="shutdown", description="Shut down the bot (Owner only).")
    async def shutdown(self, interaction: discord.Interaction):
        """Allows only the owner to shut down the bot."""
        if not await self._is_owner(interaction):
            await interaction.response.send_message("❌ You are not authorized to do this.", ephemeral=True)
            return
        await interaction.response.send_message("⚠️ Shutting down...", ephemeral=True)
        await self.bot.close()

    @app_commands.command(name="botstats", description="Show memory, CPU and ping stats.")
    async def botstats(self, interaction: discord.Interaction):
        """Displays system statistics like memory, CPU and latency."""
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(title="📊 Bot Stats", color=discord.Color.green())
        embed.add_field(name="Ping", value=f"{latency}ms", inline=True)
        embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)
        embed.add_field(name="RAM Usage", value=f"{mem.percent}%", inline=True)
        embed.set_footer(text=f"Host: {platform.node()}")

        await interaction.response.send_message(embed=embed)

    async def _is_owner(self, interaction: discord.Interaction) -> bool:
        """Internal check to confirm if user is the bot owner."""
        return interaction.user.id == self.bot.owner_id

async def setup(bot):
    await bot.add_cog(System(bot))
