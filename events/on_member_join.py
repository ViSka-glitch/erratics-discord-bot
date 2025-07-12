# --- events/on_member_join.py ---

import discord
from discord.ext import commands

class MemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Event: New Member joined ---
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        role = discord.utils.get(guild.roles, name="✅ Verified")
        log_channel = discord.utils.get(guild.text_channels, name="🔒│classified-logs")

        if role:
            try:
                await member.add_roles(role, reason="Auto-assigned on join")
                if log_channel:
                    await log_channel.send(f"✅ {member.mention} has joined and was auto-verified.")
            except discord.Forbidden:
                if log_channel:
                    await log_channel.send(f"❌ Couldn't assign Verified role to {member.mention}. Check permissions.")
        else:
            if log_channel:
                await log_channel.send("⚠️ Role '✅ Verified' not found.")

async def setup(bot):
    await bot.add_cog(MemberJoin(bot))
