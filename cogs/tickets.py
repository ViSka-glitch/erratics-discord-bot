import discord
from discord.ext import commands
from discord import ui
import io

TICKET_PANEL_CHANNEL_ID = 1393966439429312652
TICKET_LOG_CHANNEL_ID = 1394395965011791872

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = {}

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

            print(f"[DEBUG] Ticket request by {user} in guild '{guild.name}' ({guild.id}), channel: {channel.name} ({channel.id})")

            if user.id in self.active_tickets:
                print(f"[DEBUG] {user.name} already has an open ticket.")
                await interaction.response.send_message("⚠️ You already have an open ticket.", ephemeral=True)
                return

            log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

            print("[DEBUG] Creating private thread...")
            thread = await interaction.channel.create_thread(
                name=f"ticket-{user.name}",
                type=discord.ChannelType.private_thread,
                invitable=False
            )
            print(f"[DEBUG] Thread created: {thread.name} ({thread.id})")

            self.active_tickets[user.id] = thread.id

            await thread.send(f"🎟️ {user.mention}, welcome!\nPlease describe your issue here.")
            await thread.send(view=TicketCloseView(self.bot, self.active_tickets, user.id))

            if log_channel:
                await log_channel.send(f"📥 Ticket opened by {user.mention} in {thread.mention}")
                print("[DEBUG] Ticket log sent.")

            await interaction.response.send_message("✅ Your ticket has been created.", ephemeral=True)
            print("[DEBUG] Ticket interaction response sent.")

        except Exception as e:
            print(f"❌ ERROR in open_ticket: {repr(e)}")
            try:
                await interaction.response.send_message("❌ Failed to create ticket. Please contact an admin.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Failed to create ticket. Please contact an admin.", ephemeral=True)

class TicketCloseView(ui.View):
    def __init__(self, bot, active_tickets, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.active_tickets = active_tickets
        self.user_id = user_id

    @ui.button(label="🗑️ Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        try:
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
            print(f"[DEBUG] Ticket thread {thread.name} closed and deleted.")

        except Exception as e:
            print(f"❌ ERROR in close_ticket: {repr(e)}")
            try:
                await interaction.response.send_message("❌ Failed to close ticket.", ephemeral=True)
            except:
                await interaction.followup.send("❌ Failed to close ticket.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
