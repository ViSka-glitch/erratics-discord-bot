import discord
from discord.ext import commands
from discord import ui

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setticketpanel")
    @commands.has_permissions(manage_channels=True)
    async def setticketpanel(self, ctx):
        """Sendet das Ticket-Erstellungs-Panel mit Button."""
        embed = discord.Embed(
            title="🎟️ Need Help?",
            description="Click the button below to create a support ticket.\nOur team will assist you as soon as possible.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=TicketCreateView())

class TicketCreateView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        author = interaction.user

        category = discord.utils.get(guild.categories, name="🎫│support-tickets")
        support_role = discord.utils.get(guild.roles, name="🔧 Support")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True) if support_role else None
        }

        # Filter None-Einträge (falls Rolle fehlt)
        overwrites = {k: v for k, v in overwrites.items() if v is not None}

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{author.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket for {author.display_name}"
        )

        await ticket_channel.send(
            f"🎟️ {author.mention}, your ticket has been created.",
            view=TicketCloseView()
        )
        await interaction.response.send_message("✅ Ticket created.", ephemeral=True)

class TicketCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🗑️ Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        channel = interaction.channel
        await interaction.response.send_message("⚠️ Ticket will be closed in 5 seconds.", ephemeral=True)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        await channel.delete()

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
