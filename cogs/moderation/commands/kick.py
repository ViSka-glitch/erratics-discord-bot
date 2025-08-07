import discord
from config.ids import MOD_LOG_ID

async def kick_command(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.kick(reason=reason)
        await interaction.followup.send(f"👢 Kicked {member.mention}", ephemeral=True)
        log_channel = interaction.guild.get_channel(MOD_LOG_ID)
        if log_channel:
            await log_channel.send(
                f"👢 `{member}` was kicked by `{interaction.user}`.\n**Reason:** {reason}"
            )
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to kick user: {e}", ephemeral=True)
