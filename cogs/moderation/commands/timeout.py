import discord
import datetime
from config.ids import MOD_LOG_ID

async def timeout_command(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
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
