import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
import logging
import subprocess
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
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
        # Windows-Kompatibilität
        python_cmd = "python3 bot.py" if os.name != "nt" else "python bot.py"
        os.system(python_cmd)

    LOG_CHANNEL_ID = 1392804951553736717

    async def send_log_channel(self, message: str):
        channel = self.bot.get_channel(self.LOG_CHANNEL_ID)
        if channel:
            await channel.send(message)
        else:
            logging.warning(f"Log-Channel mit ID {self.LOG_CHANNEL_ID} nicht gefunden.")

    @app_commands.command(name="dump_ids", description="List all roles, channels, and categories with their IDs")
    @app_commands.checks.has_permissions(administrator=True)
    async def dump_ids(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
            return




        async def warn_duplicates(items, typ):
            names = [item.name for item in items]
            dups = set([n for n in names if names.count(n) > 1])
            if dups:
                msg = f"⚠️ Duplicate {typ} names detected: {', '.join(dups)}"
                logging.warning(msg)
                await self.send_log_channel(msg)
        await warn_duplicates(guild.categories, "category")
        await warn_duplicates(guild.text_channels, "text channel")
        await warn_duplicates(guild.voice_channels, "voice channel")
        await warn_duplicates(guild.stage_channels, "stage channel")
        if hasattr(guild, 'forum_channels'): await warn_duplicates(guild.forum_channels, "forum channel")
        if hasattr(guild, 'announcement_channels'): await warn_duplicates(guild.announcement_channels, "announcement channel")
        if hasattr(guild, 'threads'): await warn_duplicates(guild.threads, "thread")
        await warn_duplicates(guild.roles, "role")

        categories = {cat.name: cat.id for cat in guild.categories}
        text_channels = {ch.name: ch.id for ch in guild.text_channels}
        voice_channels = {ch.name: ch.id for ch in guild.voice_channels}
        stage_channels = {ch.name: ch.id for ch in guild.stage_channels}
        forum_channels = {ch.name: ch.id for ch in guild.forum_channels} if hasattr(guild, 'forum_channels') else {}
        announcement_channels = {ch.name: ch.id for ch in guild.announcement_channels} if hasattr(guild, 'announcement_channels') else {}
        threads = {thread.name: thread.id for thread in guild.threads} if hasattr(guild, 'threads') else {}
        roles = {role.name: role.id for role in guild.roles}

        output = {
            "guild_id": guild.id,
            "categories": categories,
            "text_channels": text_channels,
            "voice_channels": voice_channels,
            "stage_channels": stage_channels,
            "forum_channels": forum_channels,
            "announcement_channels": announcement_channels,
            "threads": threads,
            "roles": roles
        }

        os.makedirs("data", exist_ok=True)
        try:
            with open("data/dump_ids.json", "w") as f:
                json.dump(output, f, indent=4)
            logging.info("IDs erfolgreich exportiert.")
            await self.send_log_channel("✅ IDs erfolgreich exportiert.")
        except Exception as e:
            msg = f"❌ Fehler beim Schreiben der IDs: {e}"
            logging.error(msg)
            await self.send_log_channel(msg)
            await interaction.response.send_message(f"❌ Fehler beim Schreiben der Datei: {e}", ephemeral=True)
            return



        embed = discord.Embed(title="🧩 Server ID Dump", color=discord.Color.blue())
        embed.add_field(name="Categories", value="\n".join([f"{k}: `{v}`" for k, v in categories.items()]) or "-", inline=False)
        embed.add_field(name="Text Channels", value="\n".join([f"{k}: `{v}`" for k, v in text_channels.items()]) or "-", inline=False)
        embed.add_field(name="Voice Channels", value="\n".join([f"{k}: `{v}`" for k, v in voice_channels.items()]) or "-", inline=False)
        embed.add_field(name="Stage Channels", value="\n".join([f"{k}: `{v}`" for k, v in stage_channels.items()]) or "-", inline=False)
        embed.add_field(name="Forum Channels", value="\n".join([f"{k}: `{v}`" for k, v in forum_channels.items()]) or "-", inline=False)
        embed.add_field(name="Announcement Channels", value="\n".join([f"{k}: `{v}`" for k, v in announcement_channels.items()]) or "-", inline=False)
        embed.add_field(name="Threads", value="\n".join([f"{k}: `{v}`" for k, v in threads.items()]) or "-", inline=False)
        embed.add_field(name="Roles", value="\n".join([f"{k}: `{v}`" for k, v in roles.items()]) or "-", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="updatebot", description="Run update_and_restart.sh and show the result (Owner only)")
    @is_owner()
    async def updatebot(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            result = subprocess.run(["bash", "update_and_restart.sh"], capture_output=True, text=True, timeout=120)
            output = result.stdout[-1800:] if result.stdout else "No output."
            await interaction.followup.send(f"✅ Update script executed. Output:\n```{output}```", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error running update script: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Developer(bot))
