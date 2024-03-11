import discord
from discord.ext import commands

import datetime

class OnMessageDelete(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_message_delete")
	async def on_message_delete(self, message):
		bot = self.bot

		if message.author.bot:
			return

		if message.guild.id == 1069662276728143913:
			botLogs = bot.get_channel(1069671593174896740)
			
			deletedMessage = discord.Embed(description=f"**Message sent by {message.author.mention} deleted in {message.channel.mention}**\n{message.content}", color=discord.Color.dark_blue(), timestamp=datetime.datetime.now())
			deletedMessage.set_author(name=message.author.name, icon_url=message.author.avatar)
			deletedMessage.set_footer(text=f"Author ID: {message.author.id} | Message ID: {message.id}")
			await botLogs.send(embed=deletedMessage)



async def setup(bot):
	await bot.add_cog(OnMessageDelete(bot))