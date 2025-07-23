import discord
from discord.ext import commands
from discord import app_commands
import json
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

    @app_commands.command(name="dump_ids", description="List all roles, channels, and categories with their IDs")
    @app_commands.checks.has_permissions(administrator=True)
    async def dump_ids(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return

        categories = {cat.name: cat.id for cat in guild.categories}
        text_channels = {ch.name: ch.id for ch in guild.text_channels}
        voice_channels = {ch.name: ch.id for ch in guild.voice_channels}
        roles = {role.name: role.id for role in guild.roles if not role.is_bot_managed()}

        output = {
            "categories": categories,
            "text_channels": text_channels,
            "voice_channels": voice_channels,
            "roles": roles
        }

        os.makedirs("data", exist_ok=True)
        with open("data/dump_ids.json", "w") as f:
            json.dump(output, f, indent=4)

        embed = discord.Embed(title="🧩 Server ID Dump", color=discord.Color.blue())
        embed.add_field(name="Categories", value="\n".join([f"{k}: `{v}`" for k, v in categories.items()]) or "-", inline=False)
        embed.add_field(name="Text Channels", value="\n".join([f"{k}: `{v}`" for k, v in text_channels.items()]) or "-", inline=False)
        embed.add_field(name="Voice Channels", value="\n".join([f"{k}: `{v}`" for k, v in voice_channels.items()]) or "-", inline=False)
        embed.add_field(name="Roles", value="\n".join([f"{k}: `{v}`" for k, v in roles.items()]) or "-", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Developer(bot))
