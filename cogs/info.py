import discord
from discord.ext import commands
from discord import app_commands
import platform
import psutil

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="infobot", description="Show information about this bot.")
    async def infobot(self, interaction: discord.Interaction):
        """Displays detailed information about the bot, system and library versions."""
        embed = discord.Embed(
            title="🤖 Bot Information",
            description="Here is some technical information about the bot:",
            color=discord.Color.blue()
        )

        # Python, Library, Platform
        try:
            embed.add_field(name="Python", value=platform.python_version(), inline=True)
        except Exception as e:
            embed.add_field(name="Python", value=f"Error: {e}", inline=True)
        try:
            embed.add_field(name="Library", value=f"discord.py `{discord.__version__}`", inline=True)
        except Exception as e:
            embed.add_field(name="Library", value=f"Error: {e}", inline=True)
        try:
            embed.add_field(name="Platform", value=platform.system(), inline=True)
            embed.add_field(name="Release", value=platform.release(), inline=True)
            embed.add_field(name="Version", value=platform.version(), inline=True)
        except Exception as e:
            embed.add_field(name="Platform Info", value=f"Error: {e}", inline=True)

        # RAM
        try:
            ram = psutil.virtual_memory()
            embed.add_field(name="RAM Usage", value=f"{ram.percent}%", inline=True)
            embed.add_field(name="Total RAM", value=f"{round(ram.total / (1024**3), 2)} GB", inline=True)
            embed.add_field(name="Available RAM", value=f"{round(ram.available / (1024**3), 2)} GB", inline=True)
        except Exception as e:
            embed.add_field(name="RAM Info", value=f"Error: {e}", inline=True)

        # CPU
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)
            embed.add_field(name="CPU Cores", value=str(psutil.cpu_count(logical=True)), inline=True)
        except Exception as e:
            embed.add_field(name="CPU Info", value=f"Error: {e}", inline=True)

        # Bot Ping
        try:
            ping = round(self.bot.latency * 1000)
            embed.add_field(name="Bot Ping", value=f"{ping} ms", inline=True)
        except Exception as e:
            embed.add_field(name="Bot Ping", value=f"Error: {e}", inline=True)

        embed.set_footer(text=f"Bot ID: {getattr(self.bot.user, 'id', 'Unknown')}")

        try:
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error sending embed: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Info(bot))
