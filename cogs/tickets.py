import discord
from discord.ext import commands
from discord import ui
import io

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = {}

    @commands.Cog.listener()
    async def on_ready(self):
        channel = discord.utils.get(self.bot.get_all_channels(), name="📨│open-a-ticket")
        if not channel:
            print("❌ Channel '📨│open-a-ticket' not found.")
            return

        # Check if message already exists
        async for msg in channel.history(limit=50):
            if msg.author == self.bot.user and msg.components:
                print("✅ Ticket panel already exists.")
                return

        # Create the panel
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

        log_channel = discord.utils.get(guild.text_channels, name="ticket-logs")
        thread = await interaction.channel.create_thread(
            name=f"ticket-{user.name}",
            type=discord.ChannelType.private_thread,
            invitable=False
        )

        self.active_tickets[user.id] = thread.id

        # Send welcome message
        await thread.send(f"🎟️ {user.mention}, welcome!\nPlease describe your issue here.")
        await thread.send(view=TicketCloseView(self.bot, self.active_tickets, user.id))

        # Log ticket creation
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
        log_channel = discord.utils.get(thread.guild.text_channels, name="🔒-ticket-logs")

        await interaction.response.send_message("⚠️ Closing ticket and saving transcript...", ephemeral=True)

        # Collect transcript
        transcript = ""
        async for msg in thread.history(limit=None, oldest_first=True):
            author = msg.author.name
            content = msg.content
            transcript += f"{author}: {content}\n"

        # Send transcript
        if log_channel:
            buffer = io.BytesIO(transcript.encode("utf-8"))
            file = discord.File(fp=buffer, filename=f"{thread.name}-transcript.txt")
            await log_channel.send(f"📤 Ticket closed by {interaction.user.mention}", file=file)

        # Cleanup
        if self.user_id in self.active_tickets:
            del self.active_tickets[self.user_id]

        await thread.delete()

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
