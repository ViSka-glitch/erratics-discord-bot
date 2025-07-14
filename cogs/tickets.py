import discord
from discord.ext import commands
from discord import ui
import io

# Channel IDs (replace only if they change in Discord)
TICKET_PANEL_CHANNEL_ID = 1393966439429312652
TICKET_LOG_CHANNEL_ID = 1394395965011791872

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = {}

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.guilds[0]  # Assumes bot is in one guild; update if needed
        channel = guild.get_channel(TICKET_PANEL_CHANNEL_ID)
        if not channel:
            print(f"❌ Ticket panel channel ID {TICKET_PANEL_CHANNEL_ID} not found.")
            return

        # Avoid duplicate panel
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

class TicketCreateView(ui.View):
    def __init__(self, bot, active_tickets):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets

    @ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        user = interaction.user
        guild = interaction.guild

        if user.id in self.active_tickets:
            await interaction.response.send_message("⚠️ You already have an open ticket.", ephemeral=True)
            return

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)
        thread = await interaction.channel.create_thread(
            name=f"ticket-{user.name}",
            type=discord.ChannelType.private_thread,
            invitable=False
        )

        self.active_tickets[user.id] = thread.id

        await thread.send(f"🎟️ {user.mention}, welcome!\nPlease describe your issue here.")
        await thread.send(view=TicketCloseView(self.bot, self.active_tickets, user.id))

        if log_channel:
            await log_channel.send(f"📥 Ticket opened by {user.mention} in {thread.mention}")

        await interaction.response.send_message("✅ Your ticket has been created.", ephemeral=True)

class TicketCloseView(ui.View):
    def __init__(self, bot, active_tickets, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets
        self.user_id = user_id

    @ui.button(label="🗑️ Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        thread = interaction.channel
        log_channel = thread.guild.get_channel(TICKET_LOG_CHANNEL_ID)

        await interaction.response.send_message("⚠️ Closing ticket and saving transcript...", ephemeral=True)

        transcript = ""
        async for msg in thread.history(limit=None, oldest_first=True):
            transcript += f"{msg.created_at.strftime('%Y-%m-%d %H:%M')} - {msg.author.name}: {msg.content}\n"

        if log_channel:
            buffer = io.BytesIO(transcript.encode("utf-8"))
            file = discord.File(fp=buffer, filename=f"{thread.name}-transcript.txt")
            await log_channel.send(f"📤 Ticket closed by {interaction.user.mention}", file=file)

        if self.user_id in self.active_tickets:
            del self.active_tickets[self.user_id]

        await thread.delete()

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
