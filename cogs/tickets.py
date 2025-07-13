import discord
from discord.ext import commands
from discord import ui, app_commands

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.set_ticket_panel)

    @app_commands.command(name="setticketpanel", description="Send a ticket panel to the current channel.")
    async def set_ticket_panel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You don't have permission to do this.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎟️ Need Help?",
            description="Click the button below to create a support ticket.\nOur team will assist you as soon as possible.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=TicketCreateView(), ephemeral=True)

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
        }

        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{author.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Support ticket for {author.display_name}"
        )

        await ticket_channel.send(
            f"🎟️ {author.mention}, your ticket has been created.",
            view=TicketCloseView()
        )
        await interaction.response.send_message("✅ Your ticket has been created.", ephemeral=True)

class TicketCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🗑️ Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("⚠️ This ticket will be closed in 5 seconds...", ephemeral=True)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
        try:
            await interaction.channel.delete()
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete this channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
