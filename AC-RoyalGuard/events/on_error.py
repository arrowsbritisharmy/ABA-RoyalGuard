import discord
from discord.ext import commands

import datetime
import pytz

import discord.ext.commands.errors

from utils.utils import error_gen

class OnError(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_error")
	async def on_error(self, ctx, error):
		bot = self.bot
		error_id = error_gen()

		if isinstance(error, discord.Forbidden):
			if "Cannot send messages to this user" in str(error):
				return

		if isinstance(error, commands.CommandNotFound):
			return
		if isinstance(error, commands.CheckFailure):
			return
		if isinstance(error, commands.MissingRequiredArgument):
			return
		
		print(error)

		try:
			await bot.errors.insert(
				{
					"_id": error_id,
					"error": str(error),
					"time": datetime.datetime.now(tz=pytz.UTC).strftime(
						"%m/%d/%Y, %H:%M:%S"
					),
				}
			)
		except:
			pass



async def setup(bot):
	await bot.add_cog(OnError(bot))