import discord
import qrcode
from io import BytesIO

async def serverinvite_command(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        invite = await interaction.channel.create_invite(max_age=0, max_uses=0, unique=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Could not create invite: {e}", ephemeral=True)
        return
    try:
        qr = qrcode.make(invite.url)
    except Exception as e:
        await interaction.followup.send(f"❌ Could not generate QR code: {e}", ephemeral=True)
        return
    try:
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        file = discord.File(buffer, filename="invite_qr.png")
    except Exception as e:
        await interaction.followup.send(f"❌ Could not prepare QR code file: {e}", ephemeral=True)
        return
    embed = discord.Embed(
        title="🌐 You're invited to Erratics!",
        description=f"Join the server with [this invite link]({invite.url}) or scan the QR code below.",
        color=discord.Color.blue()
    )
    embed.set_image(url="attachment://invite_qr.png")
    embed.set_footer(text="Powered by PixelGear.gg • Gaming. Merch. Gear Up!")
    try:
        await interaction.user.send(embed=embed, file=file)
    except discord.Forbidden:
        await interaction.followup.send(
            "❌ I couldn't send you a DM. Please check your privacy settings.", ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Could not send DM: {e}", ephemeral=True)
    else:
        await interaction.followup.send("✅ Invite sent to your DMs!", ephemeral=True)
