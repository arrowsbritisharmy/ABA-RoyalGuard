import discord
from discord.ext import commands

import datetime
import pytz

import discord.ext.commands.errors

from utils.utils import error_gen

class OnCommandError(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_command_error")
	async def on_command_error(self, ctx: commands.Context, error):
		bot = self.bot
		error_id = error_gen()

		if isinstance(error, discord.Forbidden):
			if "Cannot send messages to this user" in str(error):
				return

		if isinstance(error, discord.ext.commands.errors.DisabledCommand):
			commandDisabled = discord.Embed(title = "Warning - Disabled Command", description=f"The `{ctx.command.name}` command is currently disabled. Please try again later.", color = discord.Color.dark_gold())
			commandDisabled.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=commandDisabled)
		if isinstance(error, commands.CommandOnCooldown):
			command = bot.get_command(ctx.command.name)
			rate = command._buckets._cooldown
			cooldown_amount = f"{rate.rate:.0f}"
			cooldown_length = f"{rate.per:.0f}"
			commandCooldown = discord.Embed(title = "Warning - Cooldown", description=f"You're currently on a `{cooldown_length}s` cooldown for the `{ctx.command.name}` command!", color = discord.Color.dark_gold())
			commandCooldown.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=commandCooldown)
		if isinstance(error, discord.ext.commands.errors.CommandNotFound):
			return
		if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
			return

		unexpectedError = discord.Embed(title="Error - Unexpected Error", description=f"An unexpected error occurred. Error Code: `{error_id}`", color=discord.Color.dark_red())
		unexpectedError.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		await ctx.send(embed=unexpectedError, delete_after=15)
		print(error)

		try:
			await bot.errors.insert(
				{
					"_id": error_id,
					"error": str(error),
					"time": datetime.datetime.now(tz=pytz.UTC).strftime(
						"%m/%d/%Y, %H:%M:%S"
					),
					"channel": ctx.channel.id,
					"guild": ctx.guild.id,
					"user": ctx.author.id
				}
			)
		except:
			pass



async def setup(bot):
	await bot.add_cog(OnCommandError(bot))