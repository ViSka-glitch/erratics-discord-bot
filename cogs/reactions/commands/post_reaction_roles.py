import discord

async def post_reaction_roles_command(self, ctx):
    channel_unlocker_id = 1392804917378416732
    channel = ctx.guild.get_channel(channel_unlocker_id)
    if not channel:
        await ctx.send(f"❌ Channel unlocker with ID {channel_unlocker_id} not found.")
        return
    embed = discord.Embed(title="Channel Unlocker: Game Roles",
                          description="React with the matching emoji to unlock access to the game categories!",
                          color=discord.Color.blue())
    embed.add_field(name="🧟 7 Days Outpost", value="Unlock access to 7 Days to Die", inline=False)
    embed.add_field(name="🏹 Valheim Nexus", value="Unlock access to Valheim", inline=False)
    embed.add_field(name="🚀 SE Cluster", value="Unlock access to Space Engineers", inline=False)
    msg = await channel.send(embed=embed)
    for emoji in ["🧟", "🏹", "🚀"]:
        await msg.add_reaction(emoji)
    await ctx.send(f"✅ Reaction roles message posted in channel unlocker.")
