import asyncio
import shlex
import subprocess
import os
from mcstatus import JavaServer 
import discord
from discord.ext import commands, tasks
import psutil
import time
import sys
from plexapi.server import PlexServer

intents = discord.Intents.default()
intents.message_content = True 


bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@tasks.loop(seconds=3.0)
async def monitor_server_console():
    
    if hasattr(bot, 'mc_process') and bot.mc_process.poll() is None:
        try:
            new_logs = bot.mc_process.stdout.read()
            if new_logs and new_logs.strip():
                sys.stdout.write(new_logs)
                sys.stdout.flush() 
                
            log_channel = bot.get_channel(1466652686622527569)
            if log_channel:
                await log_channel.send(f"```\n{new_logs.strip()[-1900:]}\n```")
        except (OSError, TypeError):
            pass


@bot.event
async def on_ready():
    print(f"✅ Success: {bot.user} is now monitoring your system.")
    monitor_mc_console.start() 

@bot.command(name="device-status", help="Shows device status. Includes CPU, RAM, and Battery usage/status.")
async def status(ctx):
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

@bot.command(name="mcss", help="Shows Minecraft server status. Includes player count, version, and mod loader.")
async def mc_status(ctx):
    server = JavaServer.lookup("100.85.17.2:25565")
    
    try:
        status = await server.async_status()
        
        embed = discord.Embed(title="🎮 Minecraft Server", color=discord.Color.green())
        embed.add_field(name="Status", value="✅ Online", inline=True)
        embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="Version", value=f"Minecraft {status.version.name}", inline=False)
        embed.add_field(name="Mod Loader", value="Fabric", inline=True)

        embed.set_footer(text=f"Last updated: {time.strftime('%H:%M:%S')}")
        
    except Exception:
        embed = discord.Embed(title="🎮 Minecraft Server", color=discord.Color.red())
        embed.add_field(name="Status", value="❌ Offline", inline=False)
        embed.set_footer(text="The .jar is not running.")

        embed.set_footer(text=f"Last updated: {time.strftime('%H:%M:%S')}")

    await ctx.send(embed=embed)

@bot.command(name="mods", help="Just a link to the current mod folder.")
async def mods(ctx):

    link = "https://drive.google.com/drive/folders/1ylJh8Egpt_RWwkCim219OlQTwyZP33V6?usp=sharing"
    embed = discord.Embed(title = "📂 Server Mods",
    color=discord.Color.blue()
    ) 
    embed.add_field(name="Direct Link", value=f"[Link to mods]({link})", inline=False)
    

    await ctx.send(embed=embed)

@bot.command(name="help", help="Shows a list containing commands and their functions.")
async def mods(ctx):
    embed = discord.Embed(title = "📜 Server Help",
    color=discord.Color.gold()
    ) 
    for command in bot.commands:
        if not command.hidden:
            description = command.help if command.help else "No description provided."
            embed.add_field(
                name=f"{command.name}", 
                value=description, 
                inline=False
            )

    await ctx.send(embed=embed)


@bot.command(name="ip", help="Shows server IP")
async def mods(ctx):
    embed = discord.Embed(title = "📜 Server IP",
    color=discord.Color.gold()
    ) 
    embed.add_field(
        name="IP Address", 
        value="100.85.17.2:25565", 
        inline=False
    )

    await ctx.send(embed=embed)



@bot.command(name="start-mc", help="Starts the Minecraft server.")
@commands.has_permissions(administrator=True)
async def start_minecraft(ctx):

    if hasattr(bot, 'mc_process') and bot.mc_process.poll() is None:
        await ctx.send("⚠️ Server is already running!")
        return

    await ctx.send("🚀 Starting server... monitoring logs now.")
    raw_command = "java -Xms4G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -jar server.jar nogui"
    command_list = shlex.split(raw_command)
    server_path = "/home/glad/MC-server/"

    bot.mc_process = subprocess.Popen(
        command_list,
        cwd=server_path,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    if bot.mc_process.poll() is None:
        print(f"DEBUG: Process started with PID {bot.mc_process.pid}")
    else:
        print("DEBUG: Process failed to start immediately.")
    os.set_blocking(bot.mc_process.stdout.fileno(), False)

@bot.command(name="stop-mc", help="Stops the minecraft server.")
@commands.has_permissions(administrator=True)
async def stop_minecraft(ctx):
    if hasattr(bot, 'mc_process') and bot.mc_process.poll() is None:
        await ctx.send("💾 Saving world and stopping server...")

        bot.mc_process.stdin.write("stop\n")
        bot.mc_process.stdin.flush() 
        bot.mc_process.wait(timeout=30)
        bot.mc_process = None

        await ctx.send("✅ Server stopped safely.")
    else:
        await ctx.send("❌ The server isn't running.")


@bot.command(name="ping", help="Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="console", help = "Executes game command. Usage: !console (normal game command). ")
@commands.has_role("Admin") 
async def send_console_cmd(ctx, *, mc_command: str):
    if hasattr(bot, 'mc_process') and bot.mc_process.poll() is None:
        bot.mc_process.stdin.write(f"{mc_command}\n")
        bot.mc_process.stdin.flush()

        await asyncio.sleep(0.7) 
        
        try:
            output = bot.mc_process.stdout.read()
            if output and output.strip():
                await ctx.send(f"💻 **Console Output:**\n```\n{output.strip()[-1900:]}\n```")
            else:
                await ctx.send(f"✅ Command sent, but no output received yet.")
        except Exception:
            await ctx.send(f"✅ Command sent (output buffer empty).")
    else:
        await ctx.send("❌ Server is offline.")
    

    import subprocess

@bot.command(name="terminal")
@commands.has_permissions(administrator=True)
async def terminal_access(ctx, action: str):
    action = action.lower()
    commands_map = {
        "restart": ["reboot"],
        "shutdown": ["shutdown", "now"],
        "sleep": ["systemctl", "suspend"],
    }

    if action not in commands_map:
        await ctx.send(f"❌ Invalid action. Use: `restart`, `shutdown`, `sleep`. Refer to Github page to see valid inputs.")
        return

    await ctx.send(f"⚠️ Executing system `{action}`...")
    
    try:
        subprocess.run(commands_map[action], check=True)
    except Exception as e:
        await ctx.send(f"❌ Failed to execute `{action}`: {e}")


bot.run('TOKEN')