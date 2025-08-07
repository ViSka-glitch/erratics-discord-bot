import discord
import subprocess

async def updatebot_command(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        result = subprocess.run(["bash", "update_and_restart.sh"], capture_output=True, text=True, timeout=120)
        output = result.stdout[-1800:] if result.stdout else "No output."
        await interaction.followup.send(f"✅ Update script executed. Output:\n```{output}```", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error running update script: {e}", ephemeral=True)
