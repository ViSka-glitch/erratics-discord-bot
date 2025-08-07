import discord
import json
import logging
import os

async def dump_ids_command(self, interaction: discord.Interaction):
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

    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        msg = f"❌ Error creating data directory: {e}"
        logging.error(msg)
        await self.send_log_channel(msg)
        await interaction.response.send_message(msg, ephemeral=True)
        return
    try:
        with open("data/dump_ids.json", "w") as f:
            json.dump(output, f, indent=4)
        logging.info("IDs exported successfully.")
        await self.send_log_channel("✅ IDs exported successfully.")
    except Exception as e:
        msg = f"❌ Error writing IDs: {e}"
        logging.error(msg)
        await self.send_log_channel(msg)
        await interaction.response.send_message(f"❌ Error writing file: {e}", ephemeral=True)
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
