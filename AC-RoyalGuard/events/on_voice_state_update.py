import discord
from discord.ext import commands

import datetime
import time

class OnVoiceStateUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(self, member, before, after):
        bot = self.bot

        if member.guild.id == 1069662276728143913:
            botLogs = bot.get_channel(1069671593174896740)
            if before.channel != after.channel:
                if before.channel is None:
                    vcJoin = discord.Embed(description=f"**{member.mention} joined voice channel {after.channel.mention}**", color=discord.Color.dark_blue(), timestamp=datetime.datetime.now())
                    vcJoin.set_author(name=member.name, icon_url=member.avatar)
                    vcJoin.set_footer(text=f"ID: {member.id}")
                    await botLogs.send(embed=vcJoin)
                elif after.channel is None:
                    vcLeave = discord.Embed(description=f"**{member.mention} left voice channel {before.channel.mention}**", color=discord.Color.dark_gold(), timestamp=datetime.datetime.now())
                    vcLeave.set_author(name=member.name, icon_url=member.avatar)
                    vcLeave.set_footer(text=f"ID: {member.id}")
                    await botLogs.send(embed=vcLeave)
                else:
                    vcSwitch = discord.Embed(description=f"**{member.mention} switched voice channels {before.channel.mention} -> {after.channel.mention}**", color=discord.Color.dark_blue(), timestamp=datetime.datetime.now())
                    vcSwitch.set_author(name=member.name, icon_url=member.avatar)
                    vcSwitch.set_footer(text=f"ID: {member.id}")
                    await botLogs.send(embed=vcSwitch)

                if before.channel:
                    if before.channel.id == 1069665987135295598:
                        dataset = await bot.shifts.find_by_id(member.id)
                        if dataset:
                            dataset["AFKStartTime"] = time.time()
                            await bot.shifts.upsert(dataset)
                elif after.channel:
                    if after.channel.id == 1069665987135295598:
                        dataset = await bot.shifts.find_by_id(member.id)
                        if dataset:
                            dataset["PreviousAFKTime"] = dataset["PreviousAFKTime"] + (time.time() - dataset["AFKStartTime"])
                            dataset["AFKStartTime"] = 0
                            await bot.shifts.upsert(dataset)



async def setup(bot):
    await bot.add_cog(OnVoiceStateUpdate(bot))