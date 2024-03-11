import discord
from discord.ext import commands

import datetime

class OnMemberUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before, after):
        bot = self.bot

        if before.guild.id == 1069662276728143913:
            if before.nick != after.nick:
                botLogs = bot.get_channel(1069671593174896740)
                
                nicknameChange = discord.Embed(description=f"**{after.mention} nickname changed**", color=discord.Color.dark_blue(), timestamp=datetime.datetime.now())
                nicknameChange.add_field(name="Before", value=before.nick, inline=False)
                nicknameChange.add_field(name="After", value=after.nick, inline=False)
                nicknameChange.set_author(name=after.name, icon_url=after.avatar)
                nicknameChange.set_footer(text=f"ID: {after.id}")
                await botLogs.send(embed=nicknameChange)



async def setup(bot):
    await bot.add_cog(OnMemberUpdate(bot))