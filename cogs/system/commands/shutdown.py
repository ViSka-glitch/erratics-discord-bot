async def shutdown_command(self, interaction):
    if not await self._is_owner(interaction):
        await interaction.response.send_message("❌ You are not authorized to do this.", ephemeral=True)
        return
    await interaction.response.send_message("⚠️ Shutting down...", ephemeral=True)
    await self.bot.close()
