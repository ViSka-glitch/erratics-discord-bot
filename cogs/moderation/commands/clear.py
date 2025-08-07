import discord
from config.ids import MOD_LOG_ID

async def clear_command(self, interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    if amount < 1 or amount > 100:
        await interaction.followup.send("❌ Please choose a number between 1 and 100.", ephemeral=True)
        return
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} messages.", ephemeral=True)
        log_channel = interaction.guild.get_channel(MOD_LOG_ID)
        if log_channel:
            await log_channel.send(
                f"🧹 `{interaction.user}` deleted {len(deleted)} messages in {interaction.channel.mention}"
            )
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to delete messages: {e}", ephemeral=True)
