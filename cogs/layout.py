# --- cogs/layout.py ---
import discord
from discord.ext import commands
from datetime import datetime

class LayoutSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup_layout(self, ctx):
        guild = ctx.guild
        bot_role = discord.utils.get(guild.roles, name="🤖 Bot")
        if not bot_role:
            bot_role = await guild.create_role(name="🤖 Bot", colour=discord.Colour.dark_grey())

        categories = {
            "🛰️│system": [
                ("🛰️│system-logs", "Log system events", 0),
                ("🧠│initiate-sequence", "Rules and landing", 0)
            ],
            "🌐│community": [
                ("💬│general", "Talk freely", 0),
                ("📸│media", "Share screenshots and clips", 5)
            ],
            "🔊│voice": [
                ("🔊│general-voice", None, 0)
            ]
        }

        text_perms = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            use_application_commands=True
        )
        voice_perms = discord.PermissionOverwrite(
            connect=True,
            speak=True,
            use_voice_activation=True
        )

        for category_name, channels in categories.items():
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(category_name)

            for name, topic, slowmode in channels:
                existing = discord.utils.get(category.channels, name=name)
                if existing:
                    continue

                if "voice" in name:
                    channel = await guild.create_voice_channel(name=name, category=category)
                    await channel.set_permissions(bot_role, overwrite=voice_perms)
                else:
                    channel = await guild.create_text_channel(name=name, topic=topic, slowmode_delay=slowmode, category=category)
                    await channel.set_permissions(bot_role, overwrite=text_perms)

        await ctx.send("✅ Layout erfolgreich eingerichtet.")

    @commands.command()
    async def landingpage(self, ctx):
        embed = discord.Embed(
            title="🚀 Welcome to the Server!",
            description=("Prepare yourself, Commander. You're entering a world of chaos, tech and strategy.\n"
                         "React with ✅ to accept the rules and get started."),
            color=discord.Color.orange()
        )
        embed.set_footer(text="Initiate Sequence | erratics ⚙️")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LayoutSetup(bot))
