import discord
from discord.ext import commands
import httpx
import os
import json

class JellyfinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = os.getenv("IP")
        self.base_url = f"http://{self.url}:8096"
        self.headers = {
            "X-MediaBrowser-Token": os.getenv("JELLYFIN_API_KEY"),
            "Content-Type": "application/json"
        }
        
        self.data_file = "jf-users.json"
        self._init_storage()

    def _init_storage(self):
        """Creates mapping file if missing."""
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump({}, f)

    def _get_data(self):
        with open(self.data_file, "r") as f:
            return json.load(f)

    def _save_data(self, data):
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command(name="jf-signup")
    async def signup(self, ctx, username: str):
        """Creates a passwordless JF account and maps it to your Discord UID."""
        
        discord_uid = str(ctx.author.id)
        current_mappings = self._get_data()

        if discord_uid in current_mappings:
            return await ctx.send(f"⚠️ You're already linked to: {current_mappings[discord_uid]['jf_username']}")

        endpoint = f"{self.base_url}/Users/New"
        payload = {
            "Name": username,
            "Password": "",
            "UserConfiguration": {"HideFromLoginScreens": False}
        }

        async with httpx.AsyncClient() as client:
            try:
                
                response = await client.post(endpoint, json=payload, headers=self.headers)
                response.raise_for_status()

                
                if response.status_code == 204 or not response.text:
                    return await ctx.send("✅ User created, but Jellyfin sent no ID (204). Check your dashboard!")

                data = response.json()
                jf_uid = data.get("Id")

                
                current_mappings[discord_uid] = {
                    "jf_username": username,
                    "jf_uid": jf_uid
                }
                self._save_data(current_mappings)

                await ctx.send(f"✅ Successfully created **{username}** for you!")

            except httpx.HTTPStatusError as e:
                await ctx.send(f"❌ Server Error: {e.response.status_code}. Check your API key/Firewall.")
            except json.JSONDecodeError:
                
                await ctx.send("❌ Received a non-JSON response. Jellyfin might be blocking the bot's IP.")

    @commands.command(name="jf-login", help="Logs you into the Jellyfin account")
    async def login(self, ctx, code: str):
        """Authorizes a Quick Connect code for your mapped Jellyfin account."""
        
        discord_uid = str(ctx.author.id)
        with open(self.data_file, 'r') as f:
            mappings = json.load(f)

        if discord_uid not in mappings:
            return await ctx.send("❌ You aren't linked! Use `!signup <name>` first.")

        jf_uid = mappings[discord_uid]["jf_uid"]

        endpoint = f"{self.base_url}/QuickConnect/Authorize?code={code.upper()}&userId={jf_uid}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(endpoint, headers=self.headers)
                
                if response.status_code in [200, 204]:
                    await ctx.send(f"✅ Code **{code.upper()}** authorized! Your TV should log in automatically.")
                else:
                    await ctx.send(f"❌ Failed: {response.status_code}. Is the code expired?")
            
            except Exception as e:
                await ctx.send(f"⚠️ Error connecting to Jellyfin: {str(e)}")

async def setup(bot):
    await bot.add_cog(JellyfinCog(bot))