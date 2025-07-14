import discord
from discord.ext import commands
from discord import ui

# Channel IDs (replace if changed on Discord)
WELCOME_CHANNEL_ID = 1392804912684863549
LOG_CHANNEL_ID = 1392804950320480326
QUICKSTART_CHANNEL_ID = 1392804914178166855

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        welcome_channel = guild.get_channel(WELCOME_CHANNEL_ID)
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        quickstart_channel = guild.get_channel(QUICKSTART_CHANNEL_ID)

        if not all([welcome_channel, log_channel, quickstart_channel]):
            print("❌ One or more welcome-related channels could not be found.")
            return

        embed = discord.Embed(
            title=f"👾 Welcome to {guild.name}, {member.name}!",
            description=(
                f"Prepare for upload.\n\n"
                f"To begin your integration, please confirm you're human below.\n\n"
                f"Need help? Visit {quickstart_channel.mention}."
            ),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"User ID: {member.id}")

        view = ConfirmView(member)
        await welcome_channel.send(content=member.mention, embed=embed, view=view)

        await log_channel.send(f"🟢 {member.mention} (`{member}`) joined the server.")

class ConfirmView(ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)
        self.member = member

    @ui.button(label="✅ Confirm", style=discord.ButtonStyle.green, custom_id="confirm_entry")
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message("⛔ You cannot confirm for someone else.", ephemeral=True)
            return

        await interaction.response.send_message(
            f"✅ Welcome aboard, {self.member.mention}. Your upload has been acknowledged.",
            ephemeral=True
        )
        await interaction.message.delete()

async def setup(bot):
    await bot.add_cog(Welcomer(bot))
