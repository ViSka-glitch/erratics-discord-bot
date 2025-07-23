import discord
from discord.ext import commands
from datetime import datetime
import os

from cogs.tickets import TicketCreateView, load_ticket_data  # 💡 Dateiname angepasst

LOG_CHANNEL_ID = 1392804950320480326  # 🔒│classified-logs
TRANSMISSION_ID = 1392804912684863549  # 🛁│transmission-incoming
TICKETPANEL_ID = 1393966439429312652  # 📨│open-a-ticket

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            print(f"\n✨ Checking guild: {guild.name} ({guild.id})")

            # Bot-Rolle erstellen, falls nicht vorhanden
            bot_role = discord.utils.get(guild.roles, name="🤖 Bot")
            if not bot_role:
                bot_role = await guild.create_role(name="🤖 Bot", colour=discord.Colour.dark_grey())

            # Bot-Rolle zuweisen
            bot_member = guild.get_member(self.bot.user.id)
            if bot_member and bot_role not in bot_member.roles:
                await bot_member.add_roles(bot_role)

            # Log senden
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                await log_channel.send(
                    f"🤖 Bot is online and role was assigned (`{guild.name}` at `{timestamp}`)"
                )

            # 🔍 Vorschlag A: Alle Textkanäle + IDs ausgeben
            print("\n# Text Channels:")
            for channel in guild.text_channels:
                print(f"- {channel.name}: {channel.id}")

            # 🔍 Vorschlag B: Channel-ID-Existenz prüfen
            for cid, label in [
                (TRANSMISSION_ID, "transmission-incoming"),
                (TICKETPANEL_ID, "open-a-ticket"),
                (LOG_CHANNEL_ID, "classified-logs")
            ]:
                channel = guild.get_channel(cid)
                if channel:
                    print(f"✅ Found channel ID: {cid} ({label})")
                else:
                    print(f"❌ Missing channel ID: {cid} ({label})")

            # 📆 Willkommensnachricht beim Botstart
            try:
                welcome_channel = guild.get_channel(TRANSMISSION_ID)
                if welcome_channel:
                    image_path = "/home/botuser/discord-bot/assets/erratics_welcome.png"
                    if os.path.exists(image_path):
                        file = discord.File(image_path, filename="erratics_welcome.png")
                        embed = discord.Embed(
                            title="Welcome to ERRATICS",
                            description=(
                                "You're part of something bigger now.\n"
                                "Use `/verify` to start your journey and check #🧬│initiate-sequence for details."
                            ),
                            color=discord.Color.teal()
                        )
                        embed.set_image(url="attachment://erratics_welcome.png")
                        embed.set_footer(text="Welcome, Operative.")

                        await welcome_channel.send(file=file, embed=embed)
                    else:
                        print(f"❌ Image not found: {image_path}")
                else:
                    print("❌ Welcome channel not found via ID")
            except Exception as e:
                print(f"❌ Error sending welcome embed: {e}")

        # Persistent Views für Buttons registrieren
        try:
            ticket_data = load_ticket_data()
            active_tickets = ticket_data.get("active_tickets", {})

            self.bot.add_view(TicketCreateView(self.bot, active_tickets))
            print("✅ Persistent views registered.")
        except Exception as e:
            print(f"❌ Failed to register views: {e}")

        # Slash-Commands synchronisieren
        try:
            synced = await self.bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash command(s).")
        except Exception as e:
            print(f"❌ Slash command sync failed: {e}")

        print(f"{self.bot.user} is online.")

async def setup(bot):
    if bot.get_cog("OnReady") is None:
        await bot.add_cog(OnReady(bot))
    else:
        print("⚠️ OnReady already registered – skipping.")
