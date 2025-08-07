import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, timedelta
from config.ids import GUILD_ID, WELCOME_CHANNEL_ID, VERIFY_ID, LOG_CHANNEL_ID
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
    # ...existing code...

JOIN_DATA_PATH = "data/join_pending.json"


# Modular handler imports
from .commands.verify_button import verify_button_handler
from .commands.kick_check import kick_check_handler

class VerifyView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await verify_button_handler(self, interaction, button, JOIN_DATA_PATH)

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kick_check.start()

    def cog_unload(self):
        self.kick_check.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            return

        view = VerifyView(user_id=member.id)

        embed = discord.Embed(
            title=f"Welcome, {member.name}!",
            description="Please click the button below to verify and gain access to the server.",
            color=discord.Color.orange()
        )
        file = discord.File("assets/erratics_welcome.png", filename="welcome.png")
        embed.set_image(url="attachment://welcome.png")

        try:
            message = await channel.send(
                content=member.mention,
                embed=embed,
                view=view,
                file=file
            )
            await message.edit(view=view)
            logging.info(f"Welcome message sent for {member} ({member.id}) in guild '{member.guild.name}' ({member.guild.id}).")
            log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"👋 Welcome message sent for {member.mention}.")
        except Exception as e:
            logging.error(f"Error sending welcome message for {member}: {e}")
            log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"❌ Error sending welcome message for {member.mention}: {e}")
            return

        os.makedirs(os.path.dirname(JOIN_DATA_PATH), exist_ok=True)
        if os.path.exists(JOIN_DATA_PATH):
            with open(JOIN_DATA_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[str(member.id)] = {
            "channel_id": channel.id,
            "message_id": message.id,
            "timestamp": datetime.utcnow().isoformat()
        }

        with open(JOIN_DATA_PATH, "w") as f:
            json.dump(data, f, indent=4)

    @tasks.loop(minutes=10)
    async def kick_check(self):
        await kick_check_handler(self, JOIN_DATA_PATH)

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcomer(bot))
