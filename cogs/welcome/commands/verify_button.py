import os
import json
import logging
from config.ids import VERIFY_ID, LOG_CHANNEL_ID, WELCOME_CHANNEL_ID

async def verify_button_handler(self, interaction, button, JOIN_DATA_PATH):
    if interaction.user.id != self.user_id:
        await interaction.response.send_message("This button isn't for you.", ephemeral=True)
        return
    guild = interaction.guild
    role = guild.get_role(VERIFY_ID)
    if role:
        await interaction.user.add_roles(role, reason="User verified")
    try:
        await interaction.message.delete()
    except Exception as e:
        logging.warning(f"Could not delete verify message: {e}")
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"⚠️ Could not delete verify message for {interaction.user.mention}: {e}")
    welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
    if welcome_channel:
        await welcome_channel.send(f"🎉 Welcome {interaction.user.mention} to the server!")
        logging.info(f"User {interaction.user} ({interaction.user.id}) verified and welcomed.")
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"✅ User {interaction.user.mention} verified and welcomed.")
    if os.path.exists(JOIN_DATA_PATH):
        with open(JOIN_DATA_PATH, "r") as f:
            data = json.load(f)
        data.pop(str(interaction.user.id), None)
        with open(JOIN_DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)
