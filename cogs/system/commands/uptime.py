import time
import datetime

async def uptime_command(self, interaction, start_time):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
    await interaction.response.send_message(f"🕒 Uptime: `{uptime_str}`")
