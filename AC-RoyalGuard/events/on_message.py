import discord
from discord.ext import commands

import datetime
import time

import discord.ext.commands.errors

from zuid import ZUID
error_gen = ZUID(prefix="", length=4)

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        bot = self.bot
	
        if message.author.bot:
            return
        
        """
        alfie = bot.get_user(1131274836681949254)

        if alfie.mentioned_in(message):
            if message.author.guild_permissions.administrator:
                return

            await message.delete()
            
            reason = "Pinging Alfie"
            duration = "3h"

            DM_mute = discord.Embed(title="Mute Notice", description=f"You have been muted from {message.guild.name} server.\n\nDuration : {duration}\n\nReason : {reason}", color=0x6fff3e, timestamp=datetime.datetime.now())
            
            timeoutDuration = datetime.timedelta(days=0, hours=3, minutes=0, microseconds=0)
            await message.author.timeout(timeoutDuration, reason=reason)

            try:
                await message.author.send(embed=DM_mute)
            except:
                pass

            supportChat = bot.get_channel(1069669991865126932)
            await supportChat.send(f"⚠️ {message.author.mention} | {message.author.id} - Ghost pinged Alfie in ({message.channel.mention}) and was muted for (3 hours)")

            ghostPing = discord.Embed(title = "Mute Notice", description=f"{message.author.mention} | {message.author.id} | Ghost pinged Alfie in ({message.channel.mention}) and was muted for (3 hours)", color = discord.Color.dark_gold())
            ghostPing.set_author(name=message.author.name, icon_url=message.author.avatar)
            await message.channel.send(embed=ghostPing)

            return
        """

        if 'discord.gg/' in message.content or 'discord.com/invite' in message.content:
            invite_code = None
            if 'discord.gg/' in message.content:
                invite_code = message.content.split('discord.gg/')[1].split()[0]
            elif 'discord.com/invite' in message.content:
                invite_code = message.content.split('discord.com/invite/')[1].split()[0]

            invite = await bot.fetch_invite(invite_code)

            bot_guilds = [guild.id for guild in bot.guilds]
            if invite.guild.id not in bot_guilds:
                await message.delete()
                try:
                    await message.author.send(f"{message.author.mention}, you can't send that invite in {message.guild.name}! 😡")
                except:
                    pass
        
        if message.channel.id == 1069665315044216902 or message.channel.id == 1069666252643111042:
            if not message.author.guild_permissions.administrator:
                await message.delete()



async def setup(bot):
    await bot.add_cog(OnMessage(bot))