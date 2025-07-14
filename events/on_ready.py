import discord
from discord.ext import commands
from datetime import datetime

# Channel ID for classified log channel
LOG_CHANNEL_ID = 1392804950320480326  # 🔒│classified-logs

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            # Build a dictionary of {channel_name: channel_id}
            self.bot.channel_map = {channel.name: channel.id for channel in guild.channels}
            print("✅ Channel map initialized:")
            for name, cid in self.bot.channel_map.items():
                print(f"{name}: {cid}")

            # Create bot role if it does not exist
            bot_role = discord.utils.get(guild.roles, name="🤖 Bot")
            if not bot_role:
                bot_role = await guild.create_role(name="🤖 Bot", colour=discord.Colour.dark_grey())

            # Assign bot role to the bot user
            bot_member = guild.get_member(self.bot.user.id)
            if bot_member and bot_role not in bot_member.roles:
                await bot_member.add_roles(bot_role)

            # Send log message to the log channel
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
                await log_channel.send(
                    f"🤖 Bot is online and role was assigned (`{guild.name}` at `{timestamp}`)"
                )

        # Sync slash commands
        try:
            synced = await self.bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash command(s).")
        except Exception as e:
            print(f"❌ Slash command sync failed: {e}")

        print(f"{self.bot.user} is online.")

async def setup(bot):
    await bot.add_cog(OnReady(bot))
