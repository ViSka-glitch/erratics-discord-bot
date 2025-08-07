import discord

async def post_reaction_roles_command(self, interaction):
    channel_unlocker_id = 1392804917378416732
    channel = interaction.guild.get_channel(channel_unlocker_id)
    if not channel:
        await interaction.response.send_message(f"❌ Channel unlocker with ID {channel_unlocker_id} not found.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Channel Unlocker: Game Roles",
        description="React with the matching emoji to unlock access to the game categories!",
        color=discord.Color.blue()
    )
    embed.add_field(name="🧟 7 Days Outpost", value="Unlock access to 7 Days to Die", inline=False)
    embed.add_field(name="🏹 Valheim Nexus", value="Unlock access to Valheim", inline=False)
    embed.add_field(name="🚀 SE Cluster", value="Unlock access to Space Engineers", inline=False)
    embed.add_field(name="🎮 PixelGear", value="Unlock access to PixelGear", inline=False)

    # Suche nach vorhandenem Embed im Channel
    existing_msg = None
    async for msg in channel.history(limit=50):
        if msg.author == interaction.client.user and msg.embeds:
            e = msg.embeds[0]
            if e.title == embed.title and e.description == embed.description:
                existing_msg = msg
                break

    if existing_msg:
        await existing_msg.edit(embed=embed)
        msg = existing_msg
        action = "updated"
    else:
        msg = await channel.send(embed=embed)
        action = "created"

    # Setze die gewünschten Reaktionen (nur falls sie fehlen)
    needed_emojis = ["🧟", "🏹", "🚀", "🎮"]
    existing_emojis = [str(r.emoji) for r in msg.reactions]
    for emoji in needed_emojis:
        if emoji not in existing_emojis:
            await msg.add_reaction(emoji)

    await interaction.response.send_message(f"✅ Reaction roles message {action} in channel unlocker.", ephemeral=True)
