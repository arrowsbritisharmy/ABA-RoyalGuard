import discord
from discord.ext import commands

import datetime

class OnMessageEdit(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_message_edit")
	async def on_message_edit(self, before, after):
		bot = self.bot

		if before.author.bot:
			return
	
		if before.guild.id == 1069662276728143913:
			if before.content != after.content:
				botLogs = bot.get_channel(1069671593174896740)
				
				editedMessage = discord.Embed(description=f"**Message Edited in {after.channel.mention}** [Jump to Message]({after.jump_url})", color=discord.Color.dark_gold(), timestamp=datetime.datetime.now())
				editedMessage.set_author(name=after.author.name, icon_url=after.author.avatar)
				editedMessage.add_field(name="Before", value=before.content, inline=False)
				editedMessage.add_field(name="After", value=after.content, inline=False)
				editedMessage.set_footer(text=f"User ID: {after.author.id}")
				await botLogs.send(embed=editedMessage)



async def setup(bot):
	await bot.add_cog(OnMessageEdit(bot))