import discord
from discord.ext import commands
from discord import app_commands

import inspect
from copy import copy

from menus import CustomErrorsMenu

class Developer(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(
		name='eval',
		description="eval",
		extras={"category": "Developer", "levelPermissionNeeded": float('inf')},
		with_app_command=False,
		enabled=True
	)
	async def _eval(self, ctx: commands.Context, *, code):
		result = eval(code)
		if inspect.isawaitable(result):
			result = await result
		await ctx.send(result)

	@commands.hybrid_command(
		name='sudo',
		description="No Description Specified.",
		extras={"category": "Developer", "levelPermissionNeeded": float('inf')},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(victim="The user to sudo")
	@app_commands.describe(command="The command for them to run")
	async def sudo(self, ctx: commands.Context, victim: discord.Member, *, command):
		bot = self.bot
		new_message = copy(ctx.message)
		new_message.author = victim
		new_message.content = "!" + command
		await bot.process_commands(new_message)

		successfulSudo = discord.Embed(title="Successful Sudo", description=f"Succesfully made user {victim.mention} run command !{command}", color=discord.Color.dark_blue())
		successfulSudo.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		await ctx.send(embed=successfulSudo)

	@commands.command(
		name='test',
		description="test",
		extras={"category": "Developer", "levelPermissionNeeded": 10},
		with_app_command=False,
		enabled=True
	)
	async def test(self, ctx: commands.Context):
		pass

	@commands.hybrid_group(
		name='devtools',
		extras={"category": "Developer", "levelPermissionNeeded": 10},
		with_app_command=True
	)
	async def devtools(self, ctx):
		pass

	@devtools.group()
	async def delete(self, ctx):
		pass

	@delete.command(
		name='commands',
		description='Deletes a registered slash command',
		usage="Deletes a registered slash command",
		extras={"category": "Developer", "levelPermissionNeeded": 10},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(command_name="The name of the slash command")
	async def delete_commands(self, ctx: commands.Context, command_name: str):
		bot = self.bot
		application_id = bot.user.id
		commands = await bot.http.get_global_commands(application_id)
		command = None
		for c in commands:
			if c["name"] == command_name:
				command = c
				break
		if command is not None:
			await bot.http.delete_global_command(application_id, command["id"])
			slashCommandDeleted = discord.Embed(title="Slash Command Deleted", description=f"Successfully deleted `/{command_name}` command", color=discord.Color.dark_blue())
			slashCommandDeleted.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=slashCommandDeleted)
		else:
			noCommandFound = discord.Embed(title = "Warning - Invalid Arguments", description=f"The command `/{command_name}` was not found!", color = discord.Color.dark_gold())
			noCommandFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=noCommandFound)

	@devtools.group()
	async def reload(self, ctx):
		pass

	@reload.command(
		name='commands',
		description='Reloads a command',
		usage="/devtools reload commands {command_name}",
		extras={"category": "Developer", "levelPermissionNeeded": 10},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(command_name="The name of the command")
	async def reload_commands(self, ctx: commands.Context, command_name: str):
		bot = self.bot
		command = bot.get_command(command_name)

		if command is not None:
			try:
				if command.with_app_command == True:
					commandPrefix = "/"
				else:
					commandPrefix = "!"
			except:
				commandPrefix = "!"

			try:
				await bot.reload_extension(f'cogs.{command.cog_name.lower()}')
				if commandPrefix == "/":
					slashCommandReloaded = discord.Embed(title="Slash Command Reloaded", description=f"Successfully reloaded `/{command_name}` command", color=discord.Color.dark_blue())
					slashCommandReloaded.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					return await ctx.send(embed=slashCommandReloaded)
				elif commandPrefix == "!":
					messageCommandReloaded = discord.Embed(title="Message Command Reloaded", description=f"Successfully reloaded `!{command_name}` command", color=discord.Color.dark_blue())
					messageCommandReloaded.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					return await ctx.send(embed=messageCommandReloaded)
			except:
				pass

		noCommandFound = discord.Embed(title = "Warning - Invalid Arguments", description=f"The command `{command_name}` was not found!", color = discord.Color.dark_gold())
		noCommandFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		await ctx.send(embed=noCommandFound)

	@reload.command(
		name='events',
		description='Reloads an event',
		usage="/devtools reload events {event_name}",
		extras={"category": "Developer", "levelPermissionNeeded": 10},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(event_name="The name of the event")
	async def reload_event(self, ctx: commands.Context, event_name: str):
		bot = self.bot
		try:
			await bot.reload_extension(f'events.{event_name}')

			eventReloaded = discord.Embed(title="Event Reloaded", description=f"Successfully reloaded `{event_name}` event", color=discord.Color.dark_blue())
			eventReloaded.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
			await ctx.send(embed=eventReloaded)
		except discord.ext.commands.errors.ExtensionNotLoaded:
			eventNotFound = discord.Embed(title = "Warning - Invalid Arguments", description=f"The event `{event_name}` was not found!", color = discord.Color.dark_gold())
			eventNotFound.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
			await ctx.send(embed=eventNotFound)

	@commands.hybrid_group(
		name='errors',
		extras={"category": "Developer", "levelPermissionNeeded": 0},
		with_app_command=True
	)
	async def errors(self, ctx):
		pass

	@errors.command(
		name='view',
		description='Preview an Error stored in the Database',
		usage="/errors view {error}",
		extras={"category": "Developer", "levelPermissionNeeded": float('inf')},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(error="The error ID to view")
	async def errors_view(self, ctx: commands.Context, error):
		bot = self.bot
		dataset = await bot.errors.find_by_id(error)
		if dataset:
			try:
				guildName = bot.get_guild(dataset['guild']).name
			except:
				guildName = "Unknown Server"

			viewError = discord.Embed(
					title=f"Viewing Error {error}",
					description=f"**ERROR ID:** {dataset['_id']}\n**ERROR DATE:** {dataset['time']}\n**ERROR BY:** <@{dataset['user']}>\n**ERROR INFO:** {dataset['error']}\n**SERVER:** {guildName}",
					color=discord.Color.dark_blue(),
				)
			return await ctx.send(embed=viewError)
		else:
			errorNotFound = discord.Embed(title = "Warning - Error Not Found", description=f"The error ID `{error}` was not found in our Database", color = discord.Color.dark_gold())
			errorNotFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=errorNotFound)
		
	@errors.command(
		name='delete',
		description='Delete an Error stored in the Database.',
		usage="/errors delete {error}",
		extras={"category": "Developer", "levelPermissionNeeded": float('inf')},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(error="The error ID to delete")
	async def errors_delete(self, ctx: commands.Context, error):
		bot = self.bot
		dataset = await bot.errors.find_by_id(error)
		if dataset:
			await bot.errors.delete_by_id(error)

			try:
				guildName = bot.get_guild(dataset['guild']).name
			except:
				guildName = "Unknown Server"

			errorDeleted = discord.Embed(
					title=f"Error Deleted",
					description=f"**ERROR ID:** {dataset['_id']}\n**ERROR DATE:** {dataset['time']}\n**ERROR BY:** <@{dataset['user']}>\n**ERROR INFO:** {dataset['error']}\n**SERVER:** {guildName}",
					color=discord.Color.dark_blue(),
				)
			return await ctx.send(embed=errorDeleted)
		else:
			errorNotFound = discord.Embed(title = "Warning - Error Not Found", description=f"The error ID `{error}` was not found in our Database", color = discord.Color.dark_gold())
			errorNotFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=errorNotFound)
		
	@errors.command(
		name='list',
		description='Lists all the Errors stored in the Database.',
		usage="/errors list",
		extras={"category": "Developer", "levelPermissionNeeded": float('inf')},
		with_app_command=True,
		enabled=True
	)
	async def errors_list(self, ctx: commands.Context):
		bot = self.bot
		dataset = await bot.errors.get_all()
		if dataset:
			errorServers = []

			for error in dataset:
				if error['guild'] not in errorServers:
					errorServers.append(error['guild'])

			options = [
				discord.SelectOption(
					label="All",
					description="List errors for all servers",
					value="all",
				)
			]

			for error in errorServers:
				try:
					guildName = bot.get_guild(error)
				except:
					guildName = "Unknown Server"

				options.append(
					discord.SelectOption(
						label=guildName.name,
						description=f"List errors for {guildName.name}",
						value=guildName.id,
					)
				)

			selectErrorType = discord.Embed(title=f"List Error History", description="Select the server you wish to view errors for", color=discord.Color.dark_blue())
			selectErrorType.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=selectErrorType, view=CustomErrorsMenu(ctx.author.id, options, bot))
		else:
			noErrorsFound = discord.Embed(title = "Warning - No Errors Found", description=f"There are currently no errors in our database", color = discord.Color.dark_gold())
			noErrorsFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		return await ctx.send(embed=noErrorsFound)


async def setup(bot):
	await bot.add_cog(Developer(bot))
