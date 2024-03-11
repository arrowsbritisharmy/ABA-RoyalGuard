import discord
from utils.xyron import send_request
from discord.ext import commands

class dehash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="dehash",
        description="Dehash any hash."
    )
    async def dehash(self, ctx: commands.Context, hash: str):
        bot = self.bot
        resp = await send_request('tools/hash-lookup', {
                'terms': [hash],
                "types": ["hash"]
        })
        if not resp['results']:
            return await ctx.send(embed=discord.Embed(
                title="No Results Found",
                description="There were no results found for this hash.",
                color=0xFF0000
            ))
        

        embeds = []
        for key, value in resp['results'].items():
            embed = discord.Embed(
                title=key,
                color=0x2e3136
            )
            for item in value:
                embed.add_field(name="Decrypted Hash", value=(
                    '```diff\n'
                    f'- {item["hash"]}\n'
                    f'+ {item["password"]}\n'
                    '```'
                ))
            embeds.append(embed)

        await ctx.send(embeds=embeds)


async def setup(bot: commands.Bot):
    await bot.add_cog(dehash(bot))