import discord
from discord.ext import commands
from config.ids import VERIFY_ID, LOG_CHANNEL_ID
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Constants
TARGET_EMOJI = "✅"

# Emoji zu Rollen-Mapping
ROLE_EMOJI_MAP = {
    "✅": VERIFY_ID,  # Verifizierung
    "🧟": 1402000607207886928,  # 7 Days Outpost
    "🏹": 1401999743898357952,  # Valheim Nexus
    "🚀": 1402000758697889963,  # SE Cluster
    "🎮": 1403079310998241371   # PixelGear
}


# Modular command/event handler imports
from .commands.post_reaction_roles import post_reaction_roles_command
from .commands.on_raw_reaction_add import on_raw_reaction_add_handler
from .commands.on_raw_reaction_remove import on_raw_reaction_remove_handler


from discord import app_commands

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, guild, message):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(message)
        else:
            logging.warning(f"Log channel with ID {LOG_CHANNEL_ID} not found.")

    @app_commands.command(name="post_reaction_roles", description="Post the reaction roles embed in the unlocker channel.")
    @app_commands.default_permissions(administrator=True)
    async def post_reaction_roles(self, interaction: discord.Interaction):
        await post_reaction_roles_command(self, interaction)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await on_raw_reaction_add_handler(self, payload, ROLE_EMOJI_MAP, LOG_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await on_raw_reaction_remove_handler(self, payload, ROLE_EMOJI_MAP, LOG_CHANNEL_ID)

async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))
