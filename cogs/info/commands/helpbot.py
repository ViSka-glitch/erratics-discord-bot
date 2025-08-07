import discord

async def helpbot_command(self, interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Help", color=discord.Color.green())
    embed.add_field(name="/ping", value="Replies with Pong!", inline=False)
    embed.add_field(name="/botinfo", value="Shows the bot's status and prefix.", inline=False)
    embed.add_field(name="/helpbot", value="Displays this help message.", inline=False)
    embed.add_field(name="/serverinvite", value="Creates a permanent invite link and QR code.", inline=False)
    try:
        await interaction.user.send(embed=embed)
        await interaction.response.send_message("✅ Help sent to your DMs!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I couldn't send you a DM. Please check your privacy settings.", ephemeral=True)
