import discord
from discord.ext import commands
from discord import app_commands

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _is_owner(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.bot.owner_id

    @app_commands.command(name="reload", description="Reload a specific cog. (Owner only)")
    async def reload(self, interaction: discord.Interaction, cog: str):
        if not await self._is_owner(interaction):
            await interaction.response.send_message("❌ You are not authorized to do this.", ephemeral=True)
            return

        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await self.bot.load_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"✅ Successfully reloaded `cogs.{cog}`.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to reload `cogs.{cog}`:\n```{e}```", ephemeral=True)

    @app_commands.command(name="sync", description="Manually sync all slash commands. (Owner only)")
    async def sync(self, interaction: discord.Interaction):
        if not await self._is_owner(interaction):
            await interaction.response.send_message("❌ You are not authorized to do this.", ephemeral=True)
            return

        try:
            synced = await self.bot.tree.sync()
            await interaction.response.send_message(f"✅ Synced {len(synced)} slash command(s).", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Sync failed:\n```{e}```", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Developer(bot))
