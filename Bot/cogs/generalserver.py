import discord
import time
from discord.ext import commands, tasks
import subprocess
import os
import sys
import shlex
import asyncio
import json


class ServiceManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_process = None
        self.channel = int(os.getenv("CONSOLE_CHANNEL"))
        self.server_path = os.getenv("SERVER_PATH")
        self.port = os.getenv("SERVER_PORT")
        self.active_processes = {} 
        self.config_file = "services.json"
        if not os.path.exists(self.config_file):
            print(f"[ServerManager] {self.config_file} not found. Creating template...")
            template = {
                "name": {
                    "path": "/path/to/service",
                    "start_cmd": "command",
                    "stop_cmd": "stop"
                }
            }

            with open(self.config_file, 'w') as f:
                json.dump(template, f, indent=4)

        with open(self.config_file, 'r') as f:
            self.service_config = json.load(f)

        self.monitor_server_console.start()

    def cog_unload(self):
        self.monitor_server_console.cancel()
        for process in self.active_processes.values():
            if process.poll() is None:
                process.terminate()

    @tasks.loop(seconds=3.0)
    async def monitor_server_console(self):
        for service_name in list(self.active_processes.keys()):
            process = self.active_processes[service_name]
            
            if process and process.poll() is None:
                try:
                    new_logs = process.stdout.read()
                    if new_logs:
                        print(f"[DEBUG] Read {len(new_logs)} characters from {service_name}")
                        
                        log_channel = self.bot.get_channel(self.channel)
                        if log_channel:
                            content = new_logs.strip()
                            if content:
                                chunk_size = 1900
                                for i in range(0, len(content), chunk_size):
                                    chunk = content[i:i+chunk_size]
                                    await log_channel.send(f"**[{service_name.upper()}]**\n```\n{chunk}\n```")
                        else:
                            print(f"[CRITICAL ERROR] Bot cannot find Discord channel {self.channel}!")
                            
                except BlockingIOError:
                    pass
                except Exception as e:
                    print(f"[ERROR] Exception while reading logs for {service_name}: {e}")
            
            elif process and process.poll() is not None:
                print(f"[INFO] {service_name} process died with exit code {process.poll()}")
                del self.active_processes[service_name]
                log_channel = self.bot.get_channel(self.channel)
                if log_channel:
                    await log_channel.send(f"⚠️ **[{service_name.upper()}]** process has ended (Code: {process.poll()}).")

    @monitor_server_console.error
    async def monitor_error(self, error):
        print(f"\n[CRITICAL LOOP CRASH] The monitor loop died because: {error}\n")

    @monitor_server_console.before_loop
    async def before_monitor(self):
        print("[ServiceManager] Waiting for Discord to connect...")
        await self.bot.wait_until_ready()
        print(f"[ServiceManager] Connected! Ready to send logs to channel: {self.channel}")
    
    @commands.command(name="svc-start", help="Starts a service defined in services.json. Usage: !svc-start <name>")
    @commands.has_permissions(administrator=True)
    async def svc_start(self, ctx, service_name: str):
        service_name = service_name.lower()
        
        if service_name not in self.service_config:
            await ctx.send(f"❌ '{service_name}' is not defined in `services.json`.")
            return

        if service_name in self.active_processes and self.active_processes[service_name].poll() is None:
            await ctx.send(f"⚠️ **{service_name}** is already running!")
            return

        await ctx.send(f"🚀 Starting **{service_name}**... monitoring logs now.")
        
        config = self.service_config[service_name]
        command_list = shlex.split(config["start_cmd"])

        process = subprocess.Popen(
            command_list,
            cwd=config["path"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        if process.poll() is None:
            self.active_processes[service_name] = process
            os.set_blocking(process.stdout.fileno(), False)
        else:
            await ctx.send(f"❌ Failed to start **{service_name}** immediately.")

    @commands.command(name="svc-stop", help="Stops the service. Usage: svc-stop [service-name]")
    @commands.has_permissions(administrator=True)
    async def svc_stop(self, ctx, service_name: str):
        service_name = service_name.lower()
        
        if service_name in self.active_processes and self.active_processes[service_name].poll() is None:
            process = self.active_processes[service_name]
            config = self.service_config.get(service_name, {})
            
            stop_cmd = config.get("stop_cmd", "terminate") 

            if stop_cmd.lower() in ["terminate", "kill", "sigterm"]:
                await ctx.send(f"🛑 Terminating **{service_name}** gracefully...")
                process.terminate() 
                try:
                    process.wait(timeout=10)
                    await ctx.send(f"✅ **{service_name}** terminated safely.")
                except subprocess.TimeoutExpired:
                    await ctx.send(f"⚠️ **{service_name}** is hanging. Force killing...")
                    process.kill() 
            
            else:
                await ctx.send(f"🛑 Sending stop command (`{stop_cmd}`) to **{service_name}** console...")
                process.stdin.write(f"{stop_cmd}\n")
                process.stdin.flush() 
                try:
                    process.wait(timeout=30)
                    await ctx.send(f"✅ **{service_name}** stopped safely.")
                except subprocess.TimeoutExpired:
                    await ctx.send(f"⚠️ **{service_name}** didn't stop cleanly. Terminating...")
                    process.terminate()
            
            del self.active_processes[service_name]
        else:
            await ctx.send(f"❌ **{service_name}** isn't running.")

    @commands.command(name="svc-exec", help = "Sends to stdin. Usage: !svc-exec [service] [command]. ")
    @commands.has_role("Admin") 
    async def send_console_cmd(self, ctx, service_name: str, *, server_command: str):
        service_name = service_name.lower()
        if service_name in self.active_processes and self.active_processes[service_name].poll() is None:
            process = self.active_processes[service_name]
            process.stdin.write(f"{server_command}\n")
            process.stdin.flush()

            await asyncio.sleep(0.7) 
            try:
                output = process.stdout.read()
                if output and output.strip():
                    content = output.strip()
                    chunk_size = 1900
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        await ctx.send(f"💻 **[{service_name.upper()}] Console Output:**\n```\n{chunk}\n```")
                else:
                    await ctx.send(f"✅ Command sent, but no output received yet.")
            except Exception:
                await ctx.send(f"✅ Command sent (output buffer empty).")
        else:
            await ctx.send("❌ Server is offline.")
        

    @commands.command(name="svc-status", help = "Lists every service and it's status.")
    @commands.has_role("Admin")
    async def svc_status(self, ctx):
        if not self.service_config:
            await ctx.send("❌ No services configured in `services.json`.")
            return
        status_msg = "📊 **System Service Status**\n\n"
        for service_name in self.service_config.keys():
            if service_name in self.active_processes and self.active_processes[service_name].poll() is None:
                pid = self.active_processes[service_name].pid
                status_msg += f"🟢 **{service_name.capitalize()}** `[ RUNNING ]` *(PID: {pid})*\n"
            else:
                status_msg += f"🔴 **{service_name.capitalize()}** `[ OFFLINE ]`\n"
        await ctx.send(status_msg)

async def setup(bot):
    await bot.add_cog(ServiceManager(bot))