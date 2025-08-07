import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config.ids import MOD_LOG_ID


# Modular command imports (outside the class)
from .commands.clear import clear_command
from .commands.kick import kick_command
from .commands.ban import ban_command
from .commands.timeout import timeout_command
from .commands.unban import unban_command

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_mod_commands_info(self, guild: discord.Guild):
        """Posts an embed with available mod commands to the log channel, if not already pinned."""
        log_channel = guild.get_channel(MOD_LOG_ID)
        if not log_channel:
            return

        embed = discord.Embed(
            title="🛠️ Moderation Commands",
            description=(
                "**Available Slash Commands:**\n"
                "• `/clear amount`\n"
                "• `/kick user reason`\n"
                "• `/ban user reason`\n"
                "• `/timeout user duration reason`\n"
                "• `/unban user_id reason`\n\n"
                "⚠️ Only staff with proper permissions can use these commands."
            ),
            color=discord.Color.red()
        )

        async for msg in log_channel.history(limit=10):
            if msg.author == self.bot.user and msg.embeds:
                if msg.embeds[0].title == "🛠️ Moderation Commands":
                    return  # Already posted

        msg = await log_channel.send(embed=embed)
        await msg.pin()

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.post_mod_commands_info(guild)

    @app_commands.command(name="clear", description="Delete a number of messages from the current channel.")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await clear_command(self, interaction, amount)

    @app_commands.command(name="kick", description="Kick a user from the server.")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await kick_command(self, interaction, member, reason)

    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await ban_command(self, interaction, member, reason)

    @app_commands.command(name="timeout", description="Temporarily mute a user for a number of minutes.")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
        await timeout_command(self, interaction, member, duration, reason)

    @app_commands.command(name="unban", description="Unban a user by their ID.")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        await unban_command(self, interaction, user_id, reason)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
