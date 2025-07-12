# --- cogs/basic.py ---

import discord
from discord.ext import commands
from discord import ui
from datetime import datetime
import qrcode
import io
import asyncio
from PIL import Image, ImageDraw, ImageFont

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Event: Welcome New Member ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        welcome_channel = discord.utils.get(guild.text_channels, name="📡│transmission-incoming")
        log_channel = discord.utils.get(guild.text_channels, name="🔒│classified-logs")
        quickstart_channel = discord.utils.get(guild.text_channels, name="🧬│initiate-sequence")
        role = discord.utils.get(guild.roles, name="✅ Verified")

        class AgreeView(ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @ui.button(label="I Agree ✅", style=discord.ButtonStyle.green, custom_id="agree_button")
            async def agree(self, interaction: discord.Interaction, button: ui.Button):
                if interaction.user == member and role:
                    await member.add_roles(role, reason="Agreed to rules")
                    await interaction.response.send_message("✅ You've been verified. Welcome!", ephemeral=True)
                    if log_channel:
                        await log_channel.send(f"✅ {member.mention} agreed to the rules and got the role.")
                    if quickstart_channel:
                        await member.send(f"🚀 Check out <#{quickstart_channel.id}> to get started!")
                else:
                    await interaction.response.send_message("⚠️ You can't use this button.", ephemeral=True)

        if welcome_channel:
            existing = [msg async for msg in welcome_channel.history(limit=50) if msg.author == self.bot.user and msg.components]
            if not existing:
                embed = discord.Embed(
                    title="👋 Welcome to Erratics!",
                    description=(
                        f"{member.mention}, we're glad you're here!\n\n"
                        "Please read the rules and click the button below to get access to the server."
                    ),
                    color=discord.Color.orange()
                )
                embed.add_field(name="📜 Rules", value="1. Be respectful\n2. No spam\n3. Follow Discord ToS", inline=False)
                embed.set_footer(text="PixelGear.gg • Gaming. Merch. Gear Up!")
                await welcome_channel.send(embed=embed, view=AgreeView())

    # --- Command: Ping ---
    @commands.command()
    async def ping(self, ctx):
        """Replies with Pong!"""
        await ctx.send("🏓 Pong!")

    # --- Command: Info ---
    @commands.command()
    async def info(self, ctx):
        """Displays basic bot information."""
        embed = discord.Embed(title="🤖 Bot Info", color=discord.Color.blurple())
        embed.add_field(name="Prefix", value="!", inline=True)
        embed.add_field(name="Status", value="Online", inline=True)
        embed.set_footer(text=f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        await ctx.send(embed=embed)

    # --- Command: Help ---
    @commands.command(name="helpbot")
    async def help_command(self, ctx):
        """Shows help for basic commands."""
        embed = discord.Embed(title="📖 Help", color=discord.Color.green())
        embed.add_field(name="!ping", value="Replies with Pong!", inline=False)
        embed.add_field(name="!info", value="Shows the bot's status and prefix.", inline=False)
        embed.add_field(name="!helpbot", value="Displays this help message.", inline=False)
        embed.add_field(name="!serverinvite", value="Creates a permanent invite link and QR code.", inline=False)
        await ctx.author.send(embed=embed)
        await ctx.message.delete()

    # --- Command: Server Invite ---
    @commands.command(name="serverinvite")
    @commands.has_permissions(create_instant_invite=True)
    async def server_invite(self, ctx):
        """Creates a branded invite link with QR code, interactive confirmation, and cleanup."""
        class InviteView(ui.View):
            def __init__(self, author):
                super().__init__(timeout=10)
                self.author = author
                self.value = None

            @ui.button(label="Send Invite", style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, button: ui.Button):
                if interaction.user != self.author:
                    await interaction.response.send_message("This button isn't for you.", ephemeral=True)
                    return
                self.value = True
                self.stop()
                await interaction.response.defer()

            @ui.button(label="Cancel", style=discord.ButtonStyle.red)
            async def cancel(self, interaction: discord.Interaction, button: ui.Button):
                if interaction.user != self.author:
                    await interaction.response.send_message("This button isn't for you.", ephemeral=True)
                    return
                self.value = False
                self.stop()
                await interaction.response.defer()

        guild = ctx.guild
        fixed_channel_name = "📡│transmission-incoming"
        target_channel = discord.utils.get(guild.text_channels, name=fixed_channel_name)
        log_channel = discord.utils.get(guild.text_channels, name="🔒│classified-logs")
        user = ctx.author

        view = InviteView(user)
        confirm_msg = await ctx.send("📡 Do you want to receive a server invite via DM?", view=view)

        await view.wait()
        await confirm_msg.delete()

        if not view.value:
            await ctx.send("❌ Invite cancelled.", delete_after=10)
            return

        if not target_channel:
            if log_channel:
                await log_channel.send(f"⚠️ Could not find the #{fixed_channel_name} channel.")
            return

        invite = await target_channel.create_invite(max_age=0, max_uses=0, unique=True)

        # Generate branded QR code
        qr = qrcode.make(invite.url)
        qr = qr.convert("RGB")
        width, height = qr.size
        draw = ImageDraw.Draw(qr)
        font = ImageFont.load_default()
        text = "PixelGear.gg"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.rectangle([(0, height - text_height - 10), (width, height)], fill="white")
        draw.text(((width - text_width) / 2, height - text_height - 5), text, fill="black", font=font)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        file = discord.File(fp=buffer, filename="invite_qr.png")

        try:
            embed = discord.Embed(title="🌐 You're invited to Erratics!", description=f"[Click here to join]({invite.url}) or scan the QR code below.", color=discord.Color.teal())
            embed.set_footer(text="Powered by PixelGear.gg • Gaming. Merch. Gear Up!")
            embed.set_image(url="attachment://invite_qr.png")

            await user.send(embed=embed, file=file)
            confirm = await target_channel.send(f"✅ Invite sent to {user.mention} via DM.")
            if log_channel:
                await log_channel.send(f"✅ Invite sent to {user.mention} via DM.")

            # --- Assign Verified role on invite ---
            role = discord.utils.get(guild.roles, name="✅ Verified")
            if role:
                await user.add_roles(role, reason="Invited via bot command")

            await asyncio.sleep(10)
            await ctx.message.delete()
            await confirm.delete()

        except discord.Forbidden:
            if log_channel:
                await log_channel.send(f"❌ Could not DM invite to {ctx.author.mention}. Privacy settings may block it.")


async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
