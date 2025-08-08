import json
import discord

async def se_status_command(self, interaction: discord.Interaction):
    # Only allow the bot owner to use this command
    if interaction.user.id != getattr(interaction.client, 'owner_id', None):
        await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
        return
    if not self.se_client.connected:
        await interaction.response.send_message("❌ Not connected to Space Engineers server.", ephemeral=True)
        return
    await self.se_client.send_command({"Type": "Status"})
    msg = await self.se_client.get_message(timeout=5)
    if msg:
        try:
            data = json.loads(msg)
            players = data.get("Players", [])
            await interaction.response.send_message(f"✅ SE Server online. Players: {', '.join(players) if players else 'None'}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error parsing SE response: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No response from SE server.", ephemeral=True)
