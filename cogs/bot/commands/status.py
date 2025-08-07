async def status_command(interaction):
    await interaction.response.send_message(f"✅ I'm online! {interaction.client.user} is running.")
