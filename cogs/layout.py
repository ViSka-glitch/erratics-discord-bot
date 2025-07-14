import discord
from discord.ext import commands
from discord import app_commands

class Layout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner():
        """Check if the user is the bot owner."""
        async def predicate(interaction: discord.Interaction) -> bool:
            return await interaction.client.is_owner(interaction.user)
        return app_commands.check(predicate)

    @app_commands.command(name="setup_layout", description="Create standard server layout (Owner only).")
    @is_owner()
    async def setup_layout(self, interaction: discord.Interaction):
        """Creates predefined categories and channels for the server."""
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        categories = {
            "🛰 Transmission": ["📡│transmission-incoming", "🛰️│system-logs"],
            "👤 Uplink Access": ["📨│open-a-ticket", "📃│rules", "🔧│settings"],
            "🧠 Knowledge Base": ["📚│guides", "💾│resources"],
            "🌐 General": ["💬│general", "📸│media"],
        }

        created = []

        for cat_name, channels in categories.items():
            category = discord.utils.get(guild.categories, name=cat_name)
            if not category:
                category = await guild.create_category(name=cat_name)

            for chan in channels:
                if not discord.utils.get(guild.text_channels, name=chan):
                    await guild.create_text_channel(name=chan, category=category)
                    created.append(f"#{chan}")

        await interaction.followup.send(
            f"✅ Layout created. Channels: {', '.join(created)}" if created else "⚠️ No new channels were created.",
            ephemeral=True
        )

    @app_commands.command(name="landingpage", description="Send the server landing message.")
    @is_owner()
    async def landingpage(self, interaction: discord.Interaction):
        """Sends a welcome embed in the current channel."""
        embed = discord.Embed(
            title="🚀 Welcome to the Server!",
            description=(
                "This is your digital home base.\n"
                "Read the rules in `📃│rules` and open a ticket in `📨│open-a-ticket` if you need help."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Automated Landing Page • Layout Setup")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Layout(bot))
