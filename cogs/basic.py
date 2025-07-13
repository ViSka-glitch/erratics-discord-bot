import discord
from discord.ext import commands
from datetime import datetime

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Replies with Pong!"""
        await ctx.send("🏓 Pong!")

    @commands.command()
    async def info(self, ctx):
        """Displays basic bot information."""
        embed = discord.Embed(title="🤖 Bot Info", color=discord.Color.blurple())
        embed.add_field(name="Prefix", value="!", inline=True)
        embed.add_field(name="Status", value="Online", inline=True)
        embed.set_footer(text=f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        await ctx.send(embed=embed)

    @commands.command(name="helpbot")
    async def help_command(self, ctx):
        """Shows help for basic commands."""
        embed = discord.Embed(title="📖 Help", color=discord.Color.green())
        embed.add_field(name="!ping", value="Replies with Pong!", inline=False)
        embed.add_field(name="!info", value="Shows the bot's status and prefix.", inline=False)
        embed.add_field(name="!helpbot", value="Displays this help message.", inline=False)
        embed.add_field(name="!serverinvite", value="Creates a permanent invite link and QR code.", inline=False)
        await ctx.author.send(embed=embed)
        await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(Basic(bot))
