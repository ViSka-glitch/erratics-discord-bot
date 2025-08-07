import discord
from discord import app_commands

async def reload_command(self, interaction: discord.Interaction, cog: str):
    await interaction.response.defer(ephemeral=True)
    try:
        await self.bot.reload_extension(f"cogs.{cog}")
        await interaction.followup.send(f"🔄 Reloaded `cogs.{cog}` successfully.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to reload `cogs.{cog}`: {e}", ephemeral=True)
