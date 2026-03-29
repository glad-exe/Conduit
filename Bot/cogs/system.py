import psutil
import time
import discord
from discord.ext import commands

class SystemCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="device-status", help="Shows device status. Includes CPU, RAM, and Battery usage/status.")
    async def device_status(self, ctx):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        temps = psutil.sensors_temperatures()

        if "k10temp" in temps:
            cpu_temp = round(temps['k10temp'][0].current)
        else:
            cpu_temp = "N/A"

        if battery:
            batt_percent = f"{battery.percent:.0f}%"
            batt_status = "🔌 Charging" if battery.power_plugged else "🔋 Discharging"
        else:
            batt_percent = "N/A"
            batt_status = "No Battery Detected"

        embed = discord.Embed(
            title="💻 Laptop System Monitor",
            color=discord.Color.brand_green()
        )

        embed.add_field(name="CPU Load", value=f"**{cpu_usage}%**", inline=True)
        embed.add_field(name="CPU Temp", value=f"**{cpu_temp}**", inline=True)
        embed.add_field(name="RAM Usage", value=f"**{memory.percent}%**", inline=False)
        embed.add_field(name="Battery", value=f"**{batt_percent}**\n({batt_status})", inline=False)

        embed.set_footer(text=f"Last updated: {time.strftime('%H:%M:%S')}")

        await ctx.send(embed=embed)

    @commands.command(name="help", help="Shows a list containing commands and their functions.")
    async def help_command(self, ctx):
        embed = discord.Embed(title = "📜 Server Help",
        color=discord.Color.gold()
        ) 
        for command in self.bot.commands:
            if not command.hidden:
                description = command.help if command.help else "No description provided."
                embed.add_field(
                    name=f"{command.name}", 
                    value=description, 
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="ping", help="Pong!")
    async def ping_pong(self, ctx):
        await ctx.send("Pong!")

async def setup(bot):
    await bot.add_cog(SystemCog(bot))