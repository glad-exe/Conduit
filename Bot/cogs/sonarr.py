import discord
from discord.ext import commands
import httpx
import os

class SonarrCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.api_key = os.getenv("SONAR_API_KEY")
        self.base_url = f"http://{self.bot.ip}:8989/api/v3"
        self.headers = {"X-Api-Key": self.api_key}

    @commands.command(name="srequest", help="Requests a show to be downloaded on the server.")
    async def request(self, ctx, *, show_name: str):
        print(f"DEBUG: Searching Sonarr for: {show_name}")
        
        async with httpx.AsyncClient() as client:
            try:

                search_url = f"{self.base_url}/series/lookup?term={show_name}"
                search_res = await client.get(search_url, headers=self.headers, timeout=10.0)
                
                results = search_res.json()
                print(f"DEBUG: Found {len(results)} matches.")

                if not results:
                    return await ctx.send(f"❌ Sonarr couldn't find any show named '{show_name}'.")


                best_match = results[0]
                title = best_match.get('title')
                tvdb_id = best_match.get('tvdbId')
                
                print(f"DEBUG: Best match: {title} (TVDB ID: {tvdb_id})")

                is_in_library = best_match.get('id', 0) != 0

                if is_in_library:
                    return await ctx.send(f"⚠️ **{title}** is already in your Sonarr library!")

                root_path = os.getenv("SONARR_ROOT_PATH")

                add_data = {
                "title": title,
                "tvdbId": tvdb_id,
                "qualityProfileId": 4, 
                "languageProfileId": 1,
                "rootFolderPath": root_path, 
                "monitored": True,
                "addOptions": {
                    "searchForMissingEpisodes": True,
                    "monitor": "all"
                    }
                }

                add_res = await client.post(f"{self.base_url}/series", headers=self.headers, json=add_data)

                if add_res.status_code == 201:
                    await ctx.send(f"✅ Added **{title}**! qBittorrent should start the download now. 📺")
                else:
                    error_details = add_res.json()
                    print(f"DEBUG Error: {error_details}")
                    await ctx.send(f"❌ Error adding show: `{add_res.status_code}`. Check my terminal for details.")

            except httpx.ConnectTimeout:
                await ctx.send("❌ Connection timed out. Is Sonarr reachable at '{self.bot.ip}")
            except Exception as e:
                print(f"ERROR: {e}")
                await ctx.send(f"❌ Something went wrong: `{e}`")

async def setup(bot):
    await bot.add_cog(SonarrCog(bot))