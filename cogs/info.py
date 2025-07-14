import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Display information about this server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"🛡️ {guild.name}",
            description=f"Server ID: `{guild.id}`",
            color=discord.Color.blue()
        )
        embed.add_field(name="👑 Owner", value=guild.owner.mention)
        embed.add_field(name="👥 Members", value=guild.member_count)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%Y-%m-%d %H:%M UTC"))
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Display information about a user.")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(
            title=f"👤 {member.name}",
            color=discord.Color.purple()
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="🆔 ID", value=member.id)
        embed.add_field(name="🕐 Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M UTC"))
        embed.add_field(name="🕵️ Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M UTC"))
        embed.add_field(name="💼 Top Role", value=member.top_role.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="botinfo", description="Show information about this bot.")
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Bot Info",
            color=discord.Color.green()
        )
        embed.add_field(name="🔧 Version", value="1.0")
        embed.add_field(name="💡 Commands", value=len(self.bot.tree.get_commands()))
        embed.set_footer(text=f"Running as {self.bot.user}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Show the avatar of a user.")
    async def avatar(self, interaction: discord.Interaction, user: discord.User):
        embed = discord.Embed(title=f"🖼️ Avatar: {user.name}", color=discord.Color.orange())
        embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roles", description="List all roles in this server.")
    async def roles(self, interaction: discord.Interaction):
        roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
        role_list = ", ".join([role.mention for role in roles if role.name != "@everyone"])
        embed = discord.Embed(title="📜 Server Roles", description=role_list[:4000], color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="channelinfo", description="Get information about the current channel.")
    async def channelinfo(self, interaction: discord.Interaction):
        channel = interaction.channel
        embed = discord.Embed(title=f"📺 Channel: {channel.name}", color=discord.Color.teal())
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="Type", value=str(channel.type))
        embed.add_field(name="Category", value=channel.category.name if channel.category else "None")
        embed.set_footer(text=f"Created: {channel.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="boostinfo", description="Show server boost information.")
    async def boostinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title="🚀 Server Boost Info", color=discord.Color.magenta())
        embed.add_field(name="Boost Level", value=guild.premium_tier)
        embed.add_field(name="Boost Count", value=guild.premium_subscription_count)
        boosters = [member.mention for member in guild.members if member.premium_since]
        if boosters:
            embed.add_field(name="Boosters", value=", ".join(boosters[:10]) + (" ..." if len(boosters) > 10 else ""))
        else:
            embed.add_field(name="Boosters", value="No active boosters.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
