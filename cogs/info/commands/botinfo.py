import discord
from datetime import datetime

async def botinfo_command(self, interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Bot Info", color=discord.Color.blurple())
    embed.add_field(name="Prefix", value="!", inline=True)
    embed.add_field(name="Status", value="Online", inline=True)
    embed.set_footer(text=f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await interaction.response.send_message(embed=embed)
