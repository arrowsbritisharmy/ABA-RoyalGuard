import discord
from discord.ext import commands
import aiohttp
from discord import app_commands
import typing
from utils.xyron import send_request
from utils.pagination import Pagination

class Search(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="search",
        description="Run an email through our databreach lookup engine"
    )
    # @app_commands.describe(query="The search term")
    @app_commands.describe(type="The type of data")
    async def search(self, ctx: commands.Context, query: str, type: typing.Literal[
        "Email",
        "IP Address",
        "Username",
        "Password",
        "Hash",
        "IRL Name"
    ]):
        if ctx.interaction:
            await ctx.interaction.response.defer(
                thinking=True,
                ephemeral=False
            )

        bot = self.bot
        resp = await send_request('data/search', {
                'terms': [query],
                'types': [{'Email': 'email', 'IP Address': 'lastip', 'Username': 'username', 'Password': 'password', 'Hash': 'hash', 'IRL Name': 'name'}.get(type)],
                'wildcard': False 
            })
        
        embeds = []

        for key, value in resp['results'].items():
            for item in value:
                embed = discord.Embed(
                    title=key,
                    color=discord.Color.random()
                )
                for key2, value2 in item.items():
                    hash_vars = []
                    if key2.lower() == "hash":
                        new_resp = await send_request('tools/hash-lookup', {
                                'terms': [value2],
                                "types": ["hash"]
                        })

                        try:
                            for _, value in new_resp['results'].items():
                                for item in value:
                                    hash_vars.append(item['hash'])
                                    hash_vars.append(item['password'])
                        except:
                            pass
                    
                    if len(hash_vars) == 0:
                        embed.add_field(
                            name=key2.title(),
                            value=value2,
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name=key2.title(),
                            value=(
                                f'```diff\n' + f'- {hash_vars[0]}\n' + (f'+ {hash_vars[1]}\n' if len(hash_vars) != 0 else '') + '```'
                            ),
                            inline=False
                        )
                embeds.append(embed)
        
        if len(embeds) == 0:
            return await ctx.send(embed=discord.Embed(
                title="0 Data Breaches found",
                color=0xFF0000,
                description="We have found 0 data breaches with that query."
            ))
        

        embeds[0].set_footer(text=f"Viewing page 1 / {len(embeds)}")

        await ctx.send(view=Pagination(ctx.author.id, embeds), embed=embeds[0])

async def setup(bot: commands.Bot):
    await bot.add_cog(Search(bot))