import discord
import logging

async def on_raw_reaction_add_handler(self, payload: discord.RawReactionActionEvent, ROLE_EMOJI_MAP, LOG_CHANNEL_ID):
    guild = self.bot.get_guild(payload.guild_id)
    if not guild:
        logging.warning(f"Guild with ID {payload.guild_id} not found.")
        return
    member = guild.get_member(payload.user_id)
    if not member or member.bot:
        logging.info(f"User {payload.user_id} is not a member or is a bot.")
        return
    role_id = ROLE_EMOJI_MAP.get(payload.emoji.name)
    if not role_id:
        return  # Ignore other reactions
    role = guild.get_role(role_id)
    if not role:
        await self.log_action(guild, f"❌ Role with ID {role_id} not found for emoji {payload.emoji.name}.")
        return
    try:
        await member.add_roles(role, reason=f"Reaction role via {payload.emoji.name}")
    except discord.Forbidden:
        await self.log_action(guild, f"❌ Missing permissions to assign role `{role.name}` to `{member}`.")
        return
    except Exception as e:
        await self.log_action(guild, f"❌ Error assigning role: {e}")
        logging.error(f"Error assigning role: {e}")
        return
    await self.log_action(guild, f"✅ `{member}` received the role `{role.name}` via reaction {payload.emoji.name}.")
