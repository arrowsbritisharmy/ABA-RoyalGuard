import discord
from discord.ext import commands
import aiohttp
from decouple import config
import typing
from utils.xyron import send_request

class ipinfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="ipinfo",
        description="Check the information of an IP address"
    )
    async def ipinfo(self, ctx: commands.Context, ip: str, service: typing.Literal[
        "Xyron API (Recommended)",
        "ipinfo.io"
    ]):
        bot = self.bot
        if service == "Xyron API (Recommended)":
            ip_whois_response = await send_request('tools/ip-whois', {
                'terms': [ip],
            })
            
            if len(ip_whois_response['results']) == 0:
                return await ctx.send(embed=discord.Embed(
                    title="No Results Found",
                    description="There were no results found for this hash.",
                    color=0xFF0000
                ))

            for key, value in ip_whois_response['results'].items():
                embed = discord.Embed(
                    title=key,
                    color=0x2e3136
                )
                key_map = {
                    "as": "Association",
                    "countryCode": "Country Code",
                    "isp": "Internet Service Provider",
                    "lat": "Latitude",
                    "lon": "Longitude",
                    "regionName": "Approximate Region"
                }

                for key, value in value.items():
                    embed.add_field(
                        name=(key_map.get(key) if key in key_map else key.title()),
                        value=value
                    )
                
            await ctx.send(embed=embed)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://ipinfo.io/{}/json".format(ip)) as response:
                    ip_response = await response.json()

            embed = discord.Embed(
                title=ip,
                color=0x2e3136
            )
            key_map = {
                "as": "Association",
                "countryCode": "Country Code",
                "isp": "Internet Service Provider",
                "lat": "Latitude",
                "lon": "Longitude",
                "regionName": "Approximate Region"
            }

            for key, value in ip_response.items():
                embed.add_field(
                    name=(key_map.get(key) if key in key_map else key.title()),
                    value=value
                )
                
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ipinfo(bot))