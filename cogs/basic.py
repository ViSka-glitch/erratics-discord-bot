import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Replies with Pong!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")

    @app_commands.command(name="botinfo", description="Show basic information about the bot.")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤖 Bot Info", color=discord.Color.blurple())
        embed.add_field(name="Prefix", value="!", inline=True)
        embed.add_field(name="Status", value="Online", inline=True)
        embed.set_footer(text=f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="helpbot", description="Show a help message with all basic commands.")
    async def helpbot(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 Help", color=discord.Color.green())
        embed.add_field(name="/ping", value="Replies with Pong!", inline=False)
        embed.add_field(name="/botinfo", value="Shows the bot's status and prefix.", inline=False)
        embed.add_field(name="/helpbot", value="Displays this help message.", inline=False)
        embed.add_field(name="/serverinvite", value="Creates a permanent invite link and QR code.", inline=False)
        try:
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("✅ Help sent to your DMs!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I couldn't send you a DM. Please check your privacy settings.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Basic(bot))
