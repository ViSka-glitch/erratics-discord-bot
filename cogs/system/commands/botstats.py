import discord
import psutil
import platform
import logging

async def botstats_command(self, interaction, self_ref):
    try:
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        cpu_cores = psutil.cpu_count(logical=True)
        ram_total = round(mem.total / (1024**3), 2)
        ram_available = round(mem.available / (1024**3), 2)
        ram_used = round(mem.used / (1024**3), 2)
        latency = round(self_ref.bot.latency * 1000)
        host = platform.node()
        os_name = platform.system()
        os_release = platform.release()
        os_version = platform.version()

        embed = discord.Embed(title="📊 Bot Stats", color=discord.Color.green())
        embed.add_field(name="Ping", value=f"{latency}ms", inline=True)
        embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)
        embed.add_field(name="CPU Cores", value=str(cpu_cores), inline=True)
        embed.add_field(name="RAM Usage", value=f"{mem.percent}%", inline=True)
        embed.add_field(name="RAM Total", value=f"{ram_total} GB", inline=True)
        embed.add_field(name="RAM Used", value=f"{ram_used} GB", inline=True)
        embed.add_field(name="RAM Available", value=f"{ram_available} GB", inline=True)
        embed.add_field(name="Host", value=host, inline=True)
        embed.add_field(name="OS", value=os_name, inline=True)
        embed.add_field(name="Release", value=os_release, inline=True)
        embed.add_field(name="Version", value=os_version, inline=True)
        embed.set_footer(text=f"Host: {host}")

        await interaction.response.send_message(embed=embed)

        logging.info(f"Botstats: Ping={latency}ms, CPU={cpu}%, Cores={cpu_cores}, RAM={mem.percent}%, Total={ram_total}GB, Used={ram_used}GB, Avail={ram_available}GB, Host={host}, OS={os_name}, Release={os_release}, Version={os_version}")
    except Exception as e:
        logging.error(f"Error fetching system info: {e}")
        await interaction.response.send_message(f"❌ Error fetching system info: {e}", ephemeral=True)
