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

class VerifyView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
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

        # Remove user from join_pending.json
        if os.path.exists(JOIN_DATA_PATH):
            with open(JOIN_DATA_PATH, "r") as f:
                data = json.load(f)
            data.pop(str(interaction.user.id), None)
            with open(JOIN_DATA_PATH, "w") as f:
                json.dump(data, f, indent=4)

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

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcomer(bot))
