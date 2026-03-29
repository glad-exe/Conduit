import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class ConduitBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.token = os.getenv("DISCORD_TOKEN")
        self.ip = os.getenv("IP")
        self.port = os.getenv("PORT", "25565")
        prefix = os.getenv("PREFIX", "!").strip()
        super().__init__(command_prefix=prefix, intents=intents, help_command=None)

    async def setup_hook(self):
        print("--- Initializing Modules ---")
        
        if not os.path.exists("./cogs"):
            print("Cogs not found. Are you sure the bot is running in the correct directory?")

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Loaded Cog: {filename}')
                except Exception as e:
                    print(f'❌ Failed to load {filename}: {e}')
        
        print("--- Initialization Complete ---")
    async def on_message(self, message):
        if message.author == self.user:
            return
        print(f"I heard: {message.content} from {message.author}")
        await self.process_commands(message)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Running on Arch Linux | Python {os.sys.version.split()[0]}')
        print("--------------------------------------------------")

    async def on_command_error(self, ctx, error):
        print(f"ERROR: {error}") #debugging, remove if you dont want it


async def main():    
    bot = ConduitBot()
    async with bot:
        await bot.start(bot.token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot is shutting down...")