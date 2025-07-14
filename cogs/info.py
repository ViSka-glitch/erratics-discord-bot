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

        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="Library", value=f"discord.py `{discord.__version__}`", inline=True)
        embed.add_field(name="Platform", value=platform.system(), inline=True)

        ram = psutil.virtual_memory()
        embed.add_field(name="RAM Usage", value=f"{ram.percent}%", inline=True)

        cpu = psutil.cpu_percent(interval=0.5)
        embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)

        ping = round(self.bot.latency * 1000)
        embed.add_field(name="Bot Ping", value=f"{ping} ms", inline=True)

        embed.set_footer(text=f"Bot ID: {self.bot.user.id}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
