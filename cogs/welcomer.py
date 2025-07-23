import discord
from discord.ext import commands
from discord import ui

# Channel and Role IDs
WELCOME_CHANNEL_ID = 1392804912684863549        # 📁 transmission-incoming
LOG_CHANNEL_ID = 1392804950320480326            # 🔒 classified-logs
QUICKSTART_CHANNEL_ID = 1392804914178166855     # 🧬 initiate-sequence
MEMBER_ROLE_ID = 1392804906804707369            # 🎖️ Member

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
            print("\u274c One or more welcome-related channels could not be found.")
            return

        embed = discord.Embed(
            title="\ud83d\ude3e Welcome to ERRATICS",
            description=(
                "\ud83e\udde0 *Unpredictable Gaming. Tactical Fun. True Survival.*\n\n"
                f"\ud83d\udccc Please confirm you're human to begin. Need help? Visit {quickstart_channel.mention}."
            ),
            color=discord.Color.dark_red()
        )
        embed.set_footer(text=f"User ID: {member.id} • Transmission: Initiated.")
        embed.set_image(url="attachment://erratics_welcome.png")

        view = ConfirmView(member)
        file = discord.File("/home/botuser/assets/erratics_welcome.png", filename="erratics_welcome.png")
        await welcome_channel.send(content=member.mention, embed=embed, view=view, file=file)
        await log_channel.send(f"\ud83d\udfe2 {member.mention} (`{member}`) joined the server.")

class ConfirmView(ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)
        self.member = member

    @ui.button(label="✅ Confirm", style=discord.ButtonStyle.green, custom_id="confirm_entry")
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message("⛔ You cannot confirm for someone else.", ephemeral=True)
            return

        role = interaction.guild.get_role(MEMBER_ROLE_ID)
        if role:
            try:
                await self.member.add_roles(role, reason="Confirmed entry via welcome button")
            except discord.Forbidden:
                await interaction.response.send_message("⚠️ I couldn't assign your role. Please contact staff.", ephemeral=True)
                return

        await interaction.response.send_message(
            f"✅ Welcome aboard, {self.member.mention}. Your upload has been acknowledged.",
            ephemeral=True
        )
        await interaction.message.delete()

async def setup(bot):
    await bot.add_cog(Welcomer(bot))
