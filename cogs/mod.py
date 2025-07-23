import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config.ids import MOD_LOG_ID

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
        await interaction.response.defer(ephemeral=True)
        if amount < 1 or amount > 100:
            await interaction.followup.send("❌ Please choose a number between 1 and 100.", ephemeral=True)
            return

        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} messages.", ephemeral=True)

        log_channel = interaction.guild.get_channel(MOD_LOG_ID)
        if log_channel:
            await log_channel.send(
                f"🧹 `{interaction.user}` deleted {len(deleted)} messages in {interaction.channel.mention}"
            )

    @app_commands.command(name="kick", description="Kick a user from the server.")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await interaction.response.defer(ephemeral=True)
        await member.kick(reason=reason)
        await interaction.followup.send(f"👢 Kicked {member.mention}", ephemeral=True)

        log_channel = interaction.guild.get_channel(MOD_LOG_ID)
        if log_channel:
            await log_channel.send(
                f"👢 `{member}` was kicked by `{interaction.user}`.\n**Reason:** {reason}"
            )

    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await interaction.response.defer(ephemeral=True)
        await member.ban(reason=reason)
        await interaction.followup.send(f"🔨 Banned {member.mention}", ephemeral=True)

        log_channel = interaction.guild.get_channel(MOD_LOG_ID)
        if log_channel:
            await log_channel.send(
                f"🔨 `{member}` was banned by `{interaction.user}`.\n**Reason:** {reason}"
            )

    @app_commands.command(name="timeout", description="Temporarily mute a user for a number of minutes.")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
        await interaction.response.defer(ephemeral=True)
        try:
            until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
            await member.timeout(until, reason=reason)
            await interaction.followup.send(f"⏳ {member.mention} has been timed out for {duration} minutes.", ephemeral=True)

            log_channel = interaction.guild.get_channel(MOD_LOG_ID)
            if log_channel:
                await log_channel.send(
                    f"⏳ `{member}` was timed out by `{interaction.user}` for {duration} minutes.\n**Reason:** {reason}"
                )
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to timeout user: {e}", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user by their ID.")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        await interaction.response.defer(ephemeral=True)
        try:
            user = discord.Object(id=int(user_id))
            await interaction.guild.unban(user, reason=reason)
            await interaction.followup.send(f"🕊️ User with ID `{user_id}` has been unbanned.", ephemeral=True)

            log_channel = interaction.guild.get_channel(MOD_LOG_ID)
            if log_channel:
                await log_channel.send(
                    f"🕊️ `{user_id}` was unbanned by `{interaction.user}`.\n**Reason:** {reason}"
                )
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to unban user: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
