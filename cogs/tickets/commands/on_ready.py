import discord
import logging
from config.ids import TICKET_PANEL_CHANNEL_ID
from ..tickets import TicketCreateView, save_ticket_data, load_ticket_data

async def on_ready_handler(self):
    guild = self.bot.guilds[0]
    channel = guild.get_channel(TICKET_PANEL_CHANNEL_ID)
    if not channel:
        msg = f"❌ Ticket panel channel ID {TICKET_PANEL_CHANNEL_ID} not found."
        logging.error(msg)
        await self.log_action(guild, msg)
        return
    embed = discord.Embed(
        title="🎟️ Need Support?",
        description=(
            "Click the button below to open a private support ticket."
            "Our team will respond as soon as possible."
        ),
        color=discord.Color.blurple()
    )
    panel_message_id = self.ticket_data.get("panel_message_id")
    try:
        if panel_message_id:
            msg = await channel.fetch_message(panel_message_id)
            await msg.edit(embed=embed, view=TicketCreateView(self.bot, self.active_tickets))
            logging.info("♻️ Ticket panel updated.")
            await self.log_action(guild, "♻️ Ticket panel updated.")
        else:
            raise discord.NotFound(response=None, message="No stored message ID")
    except (discord.NotFound, discord.HTTPException):
        msg = await channel.send(embed=embed, view=TicketCreateView(self.bot, self.active_tickets))
        self.ticket_data["panel_message_id"] = msg.id
        save_ticket_data(self.ticket_data)
        logging.info("📩 Ticket panel sent.")
        await self.log_action(guild, "📩 Ticket panel sent.")
