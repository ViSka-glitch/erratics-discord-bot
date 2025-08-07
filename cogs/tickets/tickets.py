import discord
from discord.ext import commands
from discord import ui, app_commands
import io
import json
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
import asyncio
from pathlib import Path
from config.ids import (
    TICKET_PANEL_CHANNEL_ID,
    TICKET_LOG_CHANNEL_ID,
    MOD_ROLE_ID,
    TICKET_ARCHIVE_CATEGORY_ID
)

TICKET_STORAGE_PATH = Path("tickets.json")
AUTO_CLOSE_MINUTES = 30
ARCHIVE_DELAY_SECONDS = 15

CATEGORY_CHOICES = {
    "valheim": {"label": "🪓 Valheim", "emoji": "🪓"},
    "space_engineers": {"label": "� Space Engineers", "emoji": "�"},
    "7d2d": {"label": "🧟 7 Days to Die", "emoji": "🧟"},
    "general": {"label": "💬 General stuff", "emoji": "💬"},
    "pixelgear": {"label": "🎮 PixelGear", "emoji": "🎮"}
}


def load_ticket_data():
    if TICKET_STORAGE_PATH.exists():
        with TICKET_STORAGE_PATH.open("r") as f:
            return json.load(f)
    return {}

def save_ticket_data(data):
    with TICKET_STORAGE_PATH.open("w") as f:
        json.dump(data, f, indent=4)

class TicketCreateView(ui.View):
    def __init__(self, bot, active_tickets):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets
        self.add_item(OpenTicketButton(bot, active_tickets))

class OpenTicketButton(ui.Button):
    def __init__(self, bot, active_tickets):
        super().__init__(label="🎫 Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
        self.bot = bot
        self.active_tickets = active_tickets

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Please select a support category:",
            view=CategorySelectView(self.bot, self.active_tickets),
            ephemeral=True
        )


# Modular event/utility handler imports
from .commands.on_ready import on_ready_handler
from .commands.log_action import log_action

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_data = load_ticket_data()
        self.active_tickets = self.ticket_data.get("active_tickets", {})

    async def log_action(self, guild, message):
        await log_action(self, guild, message)

    @commands.Cog.listener()
    async def on_ready(self):
        await on_ready_handler(self)

class CategorySelectView(ui.View):
    def __init__(self, bot, active_tickets):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets
        for key, data in CATEGORY_CHOICES.items():
            self.add_item(CategoryButton(bot, active_tickets, key, data["label"]))

class CategoryButton(ui.Button):
    def __init__(self, bot, active_tickets, category_key, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"category_{category_key}")
        self.bot = bot
        self.active_tickets = active_tickets
        self.category_key = category_key

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.channel.guild

        if str(user.id) in self.active_tickets:
            await interaction.response.send_message("⚠️ You already have an open ticket.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        try:
            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{self.category_key}-{user.name}",
                overwrites=overwrites,
                reason=f"New support ticket - {self.category_key}"
            )
        except Exception as e:
            msg = f"❌ Error creating ticket channel: {e}"
            logging.error(msg)
            log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(msg)
            await interaction.response.send_message(msg, ephemeral=True)
            return

        self.active_tickets[str(user.id)] = ticket_channel.id
        self.bot.get_cog("TicketSystem").ticket_data["active_tickets"] = self.active_tickets
        save_ticket_data(self.bot.get_cog("TicketSystem").ticket_data)

        mod_ping = f"<@&{MOD_ROLE_ID}>"
        try:
            await ticket_channel.send(
                content=f"{mod_ping} 🎫 {user.mention}, welcome!\nPlease describe your issue related to **{CATEGORY_CHOICES[self.category_key]['label']}**.",
                view=TicketCloseView(self.bot, self.active_tickets, user.id)
            )
        except Exception as e:
            msg = f"❌ Error sending welcome message in ticket: {e}"
            logging.error(msg)
            log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(msg)

        await interaction.response.send_message(f"✅ Ticket for {CATEGORY_CHOICES[self.category_key]['label']} created!", ephemeral=True)
        await self.bot.get_cog("TicketSystem").log_action(guild, f"✅ Ticket for {CATEGORY_CHOICES[self.category_key]['label']} created by {user}.")

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📅 New Ticket Opened", color=discord.Color.green())
            embed.add_field(name="User", value=f"{user} (`{user.id}`)", inline=False)
            embed.add_field(name="Category", value=self.category_key, inline=False)
            embed.add_field(name="Channel", value=ticket_channel.mention, inline=False)
            embed.add_field(name="Ticket ID", value=f"`{ticket_channel.id}`", inline=False)
            await log_channel.send(embed=embed)

        await asyncio.sleep(AUTO_CLOSE_MINUTES * 60)
        if ticket_channel and ticket_channel.id == self.active_tickets.get(str(user.id)):
            try:
                transcript = ""
                async for msg in ticket_channel.history(limit=None, oldest_first=True):
                    transcript += f"{msg.created_at.strftime('%Y-%m-%d %H:%M')} - {msg.author.name}: {msg.content}\n"

                if log_channel:
                    buffer = io.BytesIO(transcript.encode("utf-8"))
                    file = discord.File(fp=buffer, filename=f"{ticket_channel.name}-transcript.txt")
                    await log_channel.send("⏳ Ticket auto-closed due to inactivity.", file=file)

                archive_category = guild.get_channel(TICKET_ARCHIVE_CATEGORY_ID)
                await ticket_channel.edit(name=f"closed-ticket-{user.name}", category=archive_category, reason="Auto-close")

                await asyncio.sleep(5)
                overwrite = ticket_channel.overwrites_for(user)
                overwrite.view_channel = False
                await ticket_channel.set_permissions(user, overwrite=overwrite)

                del self.active_tickets[str(user.id)]
                self.bot.get_cog("TicketSystem").ticket_data["active_tickets"] = self.active_tickets
                save_ticket_data(self.bot.get_cog("TicketSystem").ticket_data)

            except Exception as e:
                msg = f"❌ ERROR during auto-close: {repr(e)}"
                logging.error(msg)
                if log_channel:
                    await log_channel.send(msg)

class TicketCloseView(ui.View):
    def __init__(self, bot, active_tickets, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets
        self.user_id = user_id
        self.add_item(CloseSolvedButton(self, solved=True))
        self.add_item(CloseSolvedButton(self, solved=False))

class CloseSolvedButton(ui.Button):
    def __init__(self, parent_view, solved):
        label = "✅ Solved" if solved else "❌ Not Solved"
        style = discord.ButtonStyle.success if solved else discord.ButtonStyle.danger
        custom_id = "close_solved" if solved else "close_unsolved"
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.parent_view = parent_view
        self.solved = solved

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CloseReasonModal(self.parent_view, self.solved, interaction.user))

class CloseReasonModal(ui.Modal):
    def __init__(self, parent_view, solved, closer):
        super().__init__(title="Close Ticket")
        self.parent_view = parent_view
        self.solved = solved
        self.closer = closer
        self.reason = ui.TextInput(
            label="Why are you closing this ticket? (optional)",
            required=False,
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = channel.guild
        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

        archive_category = guild.get_channel(TICKET_ARCHIVE_CATEGORY_ID)
        if not isinstance(archive_category, discord.CategoryChannel):
            return await interaction.response.send_message("⚠️ Ticket archive category is invalid or missing.", ephemeral=True)

        await channel.edit(name=f"closed-ticket-{self.closer.name}", category=archive_category, reason="Ticket closed")

        await interaction.response.send_message(f"✅ Ticket closed. This channel will be archived in {ARCHIVE_DELAY_SECONDS} seconds.", ephemeral=True)

        await asyncio.sleep(ARCHIVE_DELAY_SECONDS)
        member = guild.get_member(self.parent_view.user_id)
        if member:
            overwrite = channel.overwrites_for(member)
            overwrite.view_channel = False
            await channel.set_permissions(member, overwrite=overwrite)

        if str(self.parent_view.user_id) in self.parent_view.active_tickets:
            del self.parent_view.active_tickets[str(self.parent_view.user_id)]
            self.bot.get_cog("TicketSystem").ticket_data["active_tickets"] = self.parent_view.active_tickets
            save_ticket_data(self.bot.get_cog("TicketSystem").ticket_data)

        if log_channel:
            embed = discord.Embed(title="📄 Ticket Closed", color=discord.Color.red() if not self.solved else discord.Color.green())
            embed.add_field(name="Closed by", value=self.closer.mention, inline=False)
            embed.add_field(name="Status", value="✅ Solved" if self.solved else "❌ Not Solved", inline=True)
            if self.reason.value:
                embed.add_field(name="Reason", value=self.reason.value, inline=False)
            embed.add_field(name="Channel", value=channel.mention, inline=False)
            await log_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketSystem(bot))
