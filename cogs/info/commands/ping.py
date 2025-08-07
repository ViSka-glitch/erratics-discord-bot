import discord

async def ping_command(self, interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")
