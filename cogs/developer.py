import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        """Decorator to ensure only the bot owner can use the command."""
        async def predicate(interaction: discord.Interaction) -> bool:
            return await interaction.client.is_owner(interaction.user)
        return app_commands.check(predicate)

    @app_commands.command(name="reload", description="Reload a specific cog module.")
    @is_owner()
    async def reload(self, interaction: discord.Interaction, cog: str):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await interaction.followup.send(f"🔄 Reloaded `cogs.{cog}` successfully.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to reload `cogs.{cog}`: {e}", ephemeral=True)

    @app_commands.command(name="sync", description="Manually sync all slash commands.")
    @is_owner()
    async def sync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            synced = await self.bot.tree.sync()
            await interaction.followup.send(f"✅ Synced {len(synced)} command(s).", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Sync failed: {e}", ephemeral=True)

    @app_commands.command(name="restart", description="Restart the bot process (python3 bot.py).")
    @is_owner()
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message("♻️ Restarting bot...", ephemeral=True)
        await self.bot.close()
        os.system("python3 bot.py")

async def setup(bot):
    await bot.add_cog(Developer(bot))
