import logging
from config.ids import TICKET_LOG_CHANNEL_ID

async def log_action(self, guild, message):
    log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(message)
    else:
        logging.warning(f"Log-Channel mit ID {TICKET_LOG_CHANNEL_ID} nicht gefunden.")
