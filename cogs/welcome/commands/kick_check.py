import os
import json
import logging
from datetime import datetime, timedelta
from config.ids import GUILD_ID, LOG_CHANNEL_ID

async def kick_check_handler(self, JOIN_DATA_PATH):
    if not os.path.exists(JOIN_DATA_PATH):
        return
    with open(JOIN_DATA_PATH, "r") as f:
        data = json.load(f)
    to_remove = []
    for user_id, entry in data.items():
        try:
            ts = datetime.fromisoformat(entry["timestamp"])
            if datetime.utcnow() - ts > timedelta(hours=24):
                guild = self.bot.get_guild(GUILD_ID)
                member = guild.get_member(int(user_id))
                if member:
                    await member.kick(reason="Did not verify within 24h")
                    logging.info(f"❌ Kicked {member} ({member.id}) for not verifying in time.")
                    log_channel = guild.get_channel(LOG_CHANNEL_ID)
                    if log_channel:
                        await log_channel.send(f"❌ Kicked {member.mention} for not verifying in time.")
                to_remove.append(user_id)
        except Exception as e:
            logging.error(f"Error during kick check for user {user_id}: {e}")
            guild = self.bot.get_guild(GUILD_ID)
            log_channel = guild.get_channel(LOG_CHANNEL_ID) if guild else None
            if log_channel:
                await log_channel.send(f"⚠️ Error during kick check for user {user_id}: {e}")
    for uid in to_remove:
        data.pop(uid, None)
    with open(JOIN_DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)
