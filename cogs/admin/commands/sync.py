import discord
from discord import app_commands

async def sync_command(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        synced = await self.bot.tree.sync()
        await interaction.followup.send(f"✅ Synced {len(synced)} command(s).", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Sync failed: {e}", ephemeral=True)
