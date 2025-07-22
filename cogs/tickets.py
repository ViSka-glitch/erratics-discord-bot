import discord
from discord.ext import commands, tasks
from discord import ui
import io
import json
import asyncio
from pathlib import Path

TICKET_PANEL_CHANNEL_ID = 1393966439429312652
TICKET_LOG_CHANNEL_ID = 1394395965011791872
MOD_ROLE_ID = 1392804903268651104
TICKET_STORAGE_PATH = Path("tickets.json")
AUTO_CLOSE_MINUTES = 30


def load_active_tickets():
    if TICKET_STORAGE_PATH.exists():
        with TICKET_STORAGE_PATH.open("r") as f:
            return json.load(f).get("active_tickets", {})
    return {}


def save_active_tickets(tickets):
    with TICKET_STORAGE_PATH.open("w") as f:
        json.dump({"active_tickets": tickets}, f, indent=4)


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = load_active_tickets()

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.guilds[0]
        channel = guild.get_channel(TICKET_PANEL_CHANNEL_ID)
        if not channel:
            print(f"❌ Ticket panel channel ID {TICKET_PANEL_CHANNEL_ID} not found.")
            return

        async for msg in channel.history(limit=50):
            if msg.author == self.bot.user and msg.components:
                print("✅ Ticket panel already exists.")
                return

        embed = discord.Embed(
            title="🎟️ Need Support?",
            description="Click the button below to open a private support ticket.\nOur team will respond as soon as possible.",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed, view=TicketCreateView(self.bot, self.active_tickets))
        print("📨 Ticket panel sent.")


class TicketCreateView(ui.View):
    def __init__(self, bot, active_tickets):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets

    @ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        try:
            user = interaction.user
            guild = interaction.guild
            channel = interaction.channel
            log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

            if str(user.id) in self.active_tickets:
                await interaction.response.send_message("⚠️ You already have an open ticket.", ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
            }

            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{user.name}",
                overwrites=overwrites,
                reason="New support ticket"
            )

            self.active_tickets[str(user.id)] = ticket_channel.id
            save_active_tickets(self.active_tickets)

            mod_ping = f"<@&{MOD_ROLE_ID}>"
            await ticket_channel.send(f"{mod_ping} 🎟️ {user.mention}, welcome!\nPlease describe your issue here.")
            await ticket_channel.send(view=TicketCloseView(self.bot, self.active_tickets, user.id))
            await interaction.response.send_message("✅ Your ticket has been created.", ephemeral=True)

            if log_channel:
                embed = discord.Embed(title="📥 New Ticket Opened", color=discord.Color.green())
                embed.add_field(name="User", value=f"{user} (`{user.id}`)", inline=False)
                embed.add_field(name="Channel", value=ticket_channel.mention, inline=False)
                embed.add_field(name="Ticket ID", value=f"`{ticket_channel.id}`", inline=False)
                await log_channel.send(embed=embed)

            # Auto-Close Timer
            await self.start_auto_close_timer(ticket_channel, user.id, log_channel)

        except Exception as e:
            print(f"❌ ERROR in open_ticket: {repr(e)}")
            try:
                await interaction.response.send_message("❌ Failed to create ticket. Please contact an admin.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Failed to create ticket. Please contact an admin.", ephemeral=True)

    async def start_auto_close_timer(self, ticket_channel, user_id, log_channel):
        await asyncio.sleep(AUTO_CLOSE_MINUTES * 60)
        if ticket_channel and ticket_channel.id in [int(v) for v in self.active_tickets.values()]:
            try:
                transcript = ""
                async for msg in ticket_channel.history(limit=None, oldest_first=True):
                    transcript += f"{msg.created_at.strftime('%Y-%m-%d %H:%M')} - {msg.author.name}: {msg.content}\n"

                if log_channel:
                    buffer = io.BytesIO(transcript.encode("utf-8"))
                    file = discord.File(fp=buffer, filename=f"{ticket_channel.name}-transcript.txt")
                    await log_channel.send(f"⏱️ Ticket auto-closed due to inactivity.", file=file)

                await ticket_channel.delete(reason="Auto-close after inactivity")
                del self.active_tickets[str(user_id)]
                save_active_tickets(self.active_tickets)

            except Exception as e:
                print(f"❌ ERROR during auto-close: {repr(e)}")


class TicketCloseView(ui.View):
    def __init__(self, bot, active_tickets, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets
        self.user_id = user_id

    @ui.button(label="🗑️ Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        try:
            channel = interaction.channel
            log_channel = channel.guild.get_channel(TICKET_LOG_CHANNEL_ID)

            await interaction.response.send_message("⚠️ Closing ticket and saving transcript...", ephemeral=True)

            transcript = ""
            async for msg in channel.history(limit=None, oldest_first=True):
                transcript += f"{msg.created_at.strftime('%Y-%m-%d %H:%M')} - {msg.author.name}: {msg.content}\n"

            if log_channel:
                buffer = io.BytesIO(transcript.encode("utf-8"))
                file = discord.File(fp=buffer, filename=f"{channel.name}-transcript.txt")
                await log_channel.send(f"📤 Ticket closed by {interaction.user.mention}", file=file)

            if str(self.user_id) in self.active_tickets:
                del self.active_tickets[str(self.user_id)]
                save_active_tickets(self.active_tickets)

            await channel.delete()
        except Exception as e:
            print(f"❌ ERROR in close_ticket: {repr(e)}")
            try:
                await interaction.response.send_message("❌ Failed to close ticket.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Failed to close ticket.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
