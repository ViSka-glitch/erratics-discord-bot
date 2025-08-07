import discord
from config.ids import MOD_LOG_ID

async def unban_command(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
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
