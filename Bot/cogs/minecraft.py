from mcstatus import JavaServer 
import discord
import time
from discord.ext import commands, tasks
import subprocess
import os
import sys
import shlex


class MinecraftCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mc_process = None
        self.channel = int(os.getenv("CONSOLE_CHANNEL"))
        self.mc_server_path = os.getenv("MC_SERVER_PATH")
        self.port = os.getenv("PORT", "25565")

        self.monitor_server_console.start()

    def cog_unload(self):
        self.monitor_server_console.cancel()

    @tasks.loop(seconds=3.0)
    async def monitor_server_console(self):
        
        if self.mc_process and self.mc_process.poll() is None:
            try:
                new_logs = self.mc_process.stdout.read()
                if new_logs and new_logs.strip():
                    sys.stdout.write(f"[MC]{new_logs}")
                    sys.stdout.flush() 
                log_channel = self.bot.get_channel(self.channel)
                if log_channel:
                    await log_channel.send(f"```\n{new_logs.strip()[-1900:]}\n```")
            except (OSError, TypeError):
                pass

    @commands.command(name="mc-status", help="Shows Minecraft server status. Includes player count, version, and mod loader.")
    async def mc_status(self, ctx):
        #This next line pings your server ip to see if it's online. 
        #Port forwarding and/or tailscale required for it to work.
        #False positive if it's on lan, but it doesnt mean that the server is accessable.
        server = JavaServer.lookup(f"{self.bot.ip}:{self.bot.port}")
        
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

    #COMPLTELY optional command, it just helps to have it for if u wanna use modded mc 
    @commands.command(name="mc-mods", help="Just a link to the current mod folder.")
    async def mods(self, ctx):

        link = os.getenv("MODS_LINK")
        embed = discord.Embed(title = "📂 Server Mods",
        color=discord.Color.blue()
        ) 
        embed.add_field(name="Direct Link", value=f"[Link to mods]({link})", inline=False)
        

        await ctx.send(embed=embed)


    @commands.command(name="ip", help="Shows server IP")
    async def ip(self, ctx):
        embed = discord.Embed(title = "📜 Server IP",
        color=discord.Color.gold()
        ) 
        embed.add_field(
            name="IP Address", 
            value=f"{self.bot.ip}:{self.bot.port}", 
            inline=False
        )

        await ctx.send(embed=embed)



    @commands.command(name="mc-start", help="Starts the Minecraft server.")
    @commands.has_permissions(administrator=True)
    async def start_minecraft(self, ctx):

        if self.mc_process and self.mc_process.poll() is None:
            await ctx.send("⚠️ Server is already running!")
            return

        await ctx.send("🚀 Starting server... monitoring logs now.")
        raw_command = os.getenv("START_COMMAND")
        command_list = shlex.split(raw_command)

        self.mc_process = subprocess.Popen(
            command_list,
            cwd=self.mc_server_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        if self.mc_process.poll() is None:
            print(f"DEBUG: Process started with PID {self.mc_process.pid}")
        else:
            print("DEBUG: Process failed to start immediately.")
        os.set_blocking(self.mc_process.stdout.fileno(), False)

    @commands.command(name="mc-stop", help="Stops the minecraft server.")
    @commands.has_permissions(administrator=True)
    async def stop_minecraft(self, ctx):
        if self.mc_process and self.mc_process.poll() is None:
            await ctx.send("💾 Saving world and stopping server...")

            self.mc_process.stdin.write("stop\n")
            self.mc_process.stdin.flush() 
            self.mc_process.wait(timeout=30)
            self.mc_process = None

            await ctx.send("✅ Server stopped safely.")
        else:
            await ctx.send("❌ The server isn't running.")

    @commands.command(name="console", help = "Executes game command. Usage: !console [normal game command]. ")
    @commands.has_role("Admin") 
    async def send_console_cmd(self, ctx, *, mc_command: str):
        if self.mc_process and self.mc_process.poll() is None:
            self.mc_process.stdin.write(f"{mc_command}\n")
            self.mc_process.stdin.flush()

            await asyncio.sleep(0.7) 
            
            try:
                output = self.mc_process.stdout.read()
                if output and output.strip():
                    await ctx.send(f"💻 **Console Output:**\n```\n{output.strip()[-1900:]}\n```")
                else:
                    await ctx.send(f"✅ Command sent, but no output received yet.")
            except Exception:
                await ctx.send(f"✅ Command sent (output buffer empty).")
        else:
            await ctx.send("❌ Server is offline.")
        

        import subprocess


async def setup(bot):
    await bot.add_cog(MinecraftCog(bot))