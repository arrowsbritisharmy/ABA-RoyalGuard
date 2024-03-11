import discord
from discord.ext import commands

from utils.utils import colour_roles
from menus import CustomCommandsMenu
from utils.utils import calculateShiftTimes
import time
from utils.utils import timezoneRoles
import requests
import pytz
import datetime
import json
from utils.utils import client

class Miscellaneous(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.hybrid_command(
		name="oogabooga",
		description="No Description Specified.",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 10},
		with_app_command=True,
		enabled=True,
	)
	async def oogabooga(self, ctx: commands.Context):
		oogabooga = discord.Embed(title="Ooga Booga", description="Ooogggaa Booga", color=discord.Color.dark_blue())
		oogabooga.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		await ctx.send(embed=oogabooga)

	@commands.command(
		name="colour",
		aliases=['color'],
		description="colours",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True,
	)
	async def colour(self, ctx: commands.Context, colour_name: str = None):
		nitroBoosterRole = ctx.guild.get_role(1069686292876644402)

		if nitroBoosterRole not in ctx.author.roles:
			noNitro = discord.Embed(
				title="Warning - Insufficient Permissions",
				description="Only nitro boosters can use this command",
				color=discord.Color.dark_gold()
			)
			noNitro.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
			return await ctx.send(embed=noNitro)

		if ctx.guild.id != 1069662276728143913:
			return

		if colour_name is None:
			missingArguments = discord.Embed(
				title="Missing Arguments",
				description="Please include the color role you wish to join.",
				color=0xff0000
			)
			await ctx.send(f"Hello {ctx.author.mention}", embed=missingArguments, delete_after=5)
			return

		colour_name = colour_name.strip().lower().title()

		if colour_name in colour_roles:
			role = discord.utils.get(ctx.guild.roles, name=colour_name)
			for r in colour_roles:
				existing_role = discord.utils.get(ctx.author.roles, name=r)
				if existing_role:
					await ctx.author.remove_roles(existing_role)
			await ctx.author.add_roles(role)
			colourRoleJoined = discord.Embed(
				title="Color Role Joined",
				description=f"Successfully joined `{colour_name}` color role.",
				color=0x7ed513
			)
			await ctx.send(f"Hello {ctx.author.mention}", embed=colourRoleJoined, delete_after=5)
		else:
			colourRoleDoesNotExist = discord.Embed(
				title="Color Role Does Not Exist",
				description=f"The color role [{colour_name}] does not exist.",
				color=0xff0000
			)
			await ctx.send(f"Hello {ctx.author.mention}", embed=colourRoleDoesNotExist, delete_after=5)

	@commands.command(
		name="colours",
		aliases=['colors'],
		description="colours",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True,
	)
	async def colours(self, ctx: commands.Context):
		nitroBoosterRole = ctx.guild.get_role(1069686292876644402)

		if nitroBoosterRole not in ctx.author.roles:
			noNitro = discord.Embed(title="Warning - Insufficient Permissions", description="Only nitro boosters can use this command", color=discord.Color.dark_gold())
			noNitro.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
			return await ctx.send(embed=noNitro)

		if ctx.guild.id != 1069662276728143913:
			return

		colour_role_names = [name for name in colour_roles if discord.utils.get(ctx.guild.roles, name=name)]
		if len(colour_role_names) > 0:
			colour_mentions = "\n".join([f"- <@&{discord.utils.get(ctx.guild.roles, name=name).id}>" for name in colour_role_names])
			
			colours = discord.Embed(title="These are the colour roles you can choose from", description=colour_mentions, color=discord.Color.blue())
			await ctx.send(f"Hello {ctx.author.mention}", embed=colours, delete_after=5)

	@commands.command(
		name="dmannounce",
		description="dmannounce",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 10},
		with_app_command=False,
		enabled=True
	)
	async def dmannounce(self, ctx: commands.Context, member: discord.Member=None, *, text: str=None):	
		DMannouncement = discord.Embed(title="DM ANNOUNCEMENT", description=text, color=discord.Color.dark_blue())
		DMannouncement.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		if member == None:
			noMember = discord.Embed(title = "Warning - Member Not Found", description=f"The member you provided was not found. Maybe the member is not in this server or you do not specify them correctly.", color = discord.Color.dark_gold())
			noMember.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=noMember)
		elif text == None:
			noText = discord.Embed(title = "Warning - No Announcement Provided", description=f"Please provide a message to send to the user.", color = discord.Color.dark_gold())
			noText.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=noText)

		try:
			await member.send(embed=DMannouncement)
			confirmation = discord.Embed(title="DM ANNOUNCEMENT", description=f"Successfully sent DM announcement to {member.mention}", color=discord.Color.dark_blue())
			confirmation.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=confirmation)
		except:
			confirmation = discord.Embed(title="DM ANNOUNCEMENT", description=f"{member.mention} has their DMs disabled, so we were unable to send the DM announcement.", color=discord.Color.dark_blue())
			confirmation.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=confirmation)

	@commands.command(
		name="getid",
		description="getid",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True
	)
	async def getid(self, ctx: commands.Context, *, user):
		try:
			name, discriminator = user.split('#')
		except:
			userIDEmbed = discord.Embed(
				title="Discord User ID",
				description="User doesn't exist",
				color=discord.Color.dark_gold()
			)
			return await ctx.send(embed=userIDEmbed)

		try:
			user = discord.utils.get(ctx.guild.members, name=name, discriminator=discriminator)
			userIDEmbed = discord.Embed(
				title="Discord User ID",
				description=user.id,
				color=discord.Color.dark_blue()
			)
			await ctx.send(embed=userIDEmbed)
		except:
			userIDEmbed = discord.Embed(
				title="Discord User ID",
				description="User doesn't exist (failed discrim check)",
				color=discord.Color.dark_gold()
			)
			await ctx.send(embed=userIDEmbed)

	@commands.hybrid_group(
		name='shift',
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 2},
		with_app_command=True
	)
	async def shift(self, ctx):
		pass

	@shift.command(
		name='check',
		description='Check the information of your current shift',
		usage="/shift check",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 2},
		with_app_command=True,
		enabled=True
	)
	async def shift_check(self, ctx: commands.Context):
		bot = self.bot
		dataset = await bot.shifts.find_by_id(ctx.author.id)
		if dataset:
			shiftTime, AFKTime, totalTime = calculateShiftTimes(dataset)
			shiftCheck = discord.Embed(title="Shift Check", description=f"Showing current shift statistics\n\nShift Time: {shiftTime}\nAFK Time: {AFKTime}\nTotal Time: {totalTime}", color=discord.Color.dark_gold())
			shiftCheck.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=shiftCheck, ephemeral=True)
		else:
			noShiftFound = discord.Embed(title="Shift Check", description="There is no current shift found for you, please start one using `/shift start`", color=discord.Color.dark_gold())
			noShiftFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=noShiftFound)

	@shift.command(
		name='end',
		description='Ends a current shift',
		usage="/shift end",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 2},
		with_app_command=True,
		enabled=True
	)
	async def shift_end(self, ctx: commands.Context):
		bot = self.bot
		dataset = await bot.shifts.find_by_id(ctx.author.id)
		if dataset:
			shiftTime, AFKTime, totalTime = calculateShiftTimes(dataset)
			shiftCheck = discord.Embed(title="Shift End", description=f"Successfully ended your current shift\n\nShift Time: {shiftTime}\nAFK Time: {AFKTime}\nTotal Time: {totalTime}", color=discord.Color.dark_gold())
			shiftCheck.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=shiftCheck, ephemeral=True)
			await bot.shifts.delete_by_id(ctx.author.id)
		else:
			noShiftFound = discord.Embed(title="Shift End", description="There is no current shift found for you, please start one using `/shift start`", color=discord.Color.dark_gold())
			noShiftFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=noShiftFound)

	@shift.command(
		name='start',
		description='Starts a new shift',
		usage="/shift start",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 2},
		with_app_command=True,
		enabled=True
	)
	async def shift_start(self, ctx: commands.Context):
		bot = self.bot
		dataset = await bot.shifts.find_by_id(ctx.author.id)
		if dataset:
			shiftFound = discord.Embed(title="Shift Start", description="There is a current shift found for you, to start a new shift please end it using `/shift end`", color=discord.Color.dark_gold())
			shiftFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=shiftFound, ephemeral=True)
		
		mainCall = discord.utils.get(ctx.guild.channels, id=1069665987135295598)
		for channel in ctx.guild.voice_channels:
			if ctx.author in channel.members:
				if ctx.author.voice.channel == mainCall:
					shiftItem = {
						'_id': ctx.author.id,
							"ShiftStartTime": time.time(),
							"AFKStartTime": 0,
							"PreviousAFKTime": 0,
					}
					await bot.shifts.insert(shiftItem)

					shiftStarted = discord.Embed(title="Shift Start", description="Successfully started a new shift", color=discord.Color.dark_gold())
					shiftStarted.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					return await ctx.send(embed=shiftStarted, ephemeral=True)

		joinMainCall = discord.Embed(title="Shift Start", description="Please join the main voice channel to begin your shift!", color=discord.Color.dark_gold())
		joinMainCall.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		return await ctx.send(embed=joinMainCall)
	
	@commands.command(
		name="aest",
		description="aest",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True
	)
	async def aest(self, ctx: commands.Context):
		bot = self.bot
		timezoneRoleJoined = discord.Embed(title="Timezone Role Joined", description=f"Successfully joined `{ctx.command.name.upper()}` timezone role.", color=0x7ed513)
		await ctx.send(f"Hello {ctx.author.mention}", embed=timezoneRoleJoined, delete_after=5)

		for guild in bot.guilds:
			member = guild.get_member(ctx.author.id)
			if member:
				for role in timezoneRoles:
					timezoneRole = discord.utils.get(ctx.guild.roles, name=role)
					if timezoneRole and timezoneRole in ctx.author.roles:
						await ctx.author.remove_roles(timezoneRole)
				timezoneRole = discord.utils.get(ctx.guild.roles, name=ctx.command.name.upper())
				if timezoneRole and timezoneRole not in ctx.author.roles:
					await ctx.author.add_roles(timezoneRole)

	@commands.command(
		name="est",
		description="est",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True
	)
	async def est(self, ctx: commands.Context):
		bot = self.bot
		timezoneRoleJoined = discord.Embed(title="Timezone Role Joined", description=f"Successfully joined `{ctx.command.name.upper()}` timezone role.", color=0x7ed513)
		await ctx.send(f"Hello {ctx.author.mention}", embed=timezoneRoleJoined, delete_after=5)

		for guild in bot.guilds:
			member = guild.get_member(ctx.author.id)
			if member:
				for role in timezoneRoles:
					timezoneRole = discord.utils.get(ctx.guild.roles, name=role)
					if timezoneRole and timezoneRole in ctx.author.roles:
						await ctx.author.remove_roles(timezoneRole)
				timezoneRole = discord.utils.get(ctx.guild.roles, name=ctx.command.name.upper())
				if timezoneRole and timezoneRole not in ctx.author.roles:
					await ctx.author.add_roles(timezoneRole)

	@commands.command(
		name="gmt",
		description="gmt",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True
	)
	async def gmt(self, ctx: commands.Context):
		bot = self.bot
		timezoneRoleJoined = discord.Embed(title="Timezone Role Joined", description=f"Successfully joined `{ctx.command.name.upper()}` timezone role.", color=0x7ed513)
		await ctx.send(f"Hello {ctx.author.mention}", embed=timezoneRoleJoined, delete_after=5)

		for guild in bot.guilds:
			member = guild.get_member(ctx.author.id)
			if member:
				for role in timezoneRoles:
					timezoneRole = discord.utils.get(ctx.guild.roles, name=role)
					if timezoneRole and timezoneRole in ctx.author.roles:
						await ctx.author.remove_roles(timezoneRole)
				timezoneRole = discord.utils.get(ctx.guild.roles, name=ctx.command.name.upper())
				if timezoneRole and timezoneRole not in ctx.author.roles:
					await ctx.author.add_roles(timezoneRole)

	@commands.command(
		name="bgcheck",
		description="bgcheck",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True
	)
	async def bgcheck(self, ctx: commands.Context, member: discord.Member=None):
		bot = self.bot
		if member == None:
			member = ctx.message.author
		rolelist = [r.mention for r in member.roles if r != ctx.guild.default_role]
		rolesBGcheck = "\n".join(rolelist)
		inProgress = discord.Embed(title="Background Checking", description="Please hold on whilst we background check the user.", color=discord.Color.blue())
		backgroundCheck = await ctx.send(f"Hello {ctx.message.author.mention}", embed=inProgress, delete_after=30)

		joinedAt = str(ctx.author.joined_at)
		size = len(joinedAt)
		newJoinedAt = joinedAt[:size - 6]

		dayOfMonth = member.joined_at.strftime("%B")
		firstDigitsOfMonth = dayOfMonth[0:3]
		FDOM = firstDigitsOfMonth

		dataset = await bot.roblox.find_by_id(member.id)

		if not dataset:
			notVerified = discord.Embed(title="Background Check", description="This user is not verified", color=0xff0000)
			notVerified.set_footer(text=f"Royal Guard 2023", icon_url="")
			return await backgroundCheck.edit(embed=notVerified, delete_after=5)

		robloxID = dataset['roblox']

		response = requests.get(f'https://groups.roblox.com/v1/users/{robloxID}/groups/roles')
		group_roles = json.loads(response.content)['data']

		alerts = []

		blacklisted_groups = [2621202, 4972535, 6052143, 17242178]
		whitelisted_groups = [15356653]
		blacklisted_names = ["British Army"]
		detected_groups = [f"{' > B' if role['group']['id'] in blacklisted_groups else ' > D'} | [{role['group']['name']} - Owned by {role['group']['owner']['username']}]" for role in group_roles if role['group']['id'] not in whitelisted_groups and (role['group']['id'] in blacklisted_groups or any(name in role['group']['name'] for name in blacklisted_names))]
		if detected_groups:
			detected_groups_text = "\n".join(detected_groups)
			alerts.append(f"\n- ⚠️ [This user is in some detected groups.] ⚠️\n\n{detected_groups_text}")

		account_created_at = member.created_at
		account_created_at = account_created_at.replace(tzinfo=pytz.UTC)
		current_time = datetime.datetime.now(pytz.UTC)
		time_diff = current_time - account_created_at
		if time_diff.days < 30:
			alerts.append("\n- ⚠️ [This user Discord account age is lesser then the recommended amount 30 days.] ⚠️")

		created_at = member.created_at
		joined_at = member.joined_at
		now = datetime.datetime.now()

		created_at = created_at.replace(tzinfo=None)
		joined_at = joined_at.replace(tzinfo=None)
		now = now.replace(tzinfo=None)

		delta = joined_at - created_at
		if delta.total_seconds() <= 3600:
			alerts.append("\n- ⚠️ [This user joined the British Army Discord within one hour of registering the Discord Account.] ⚠️")

		robloxUser = await client.get_user(robloxID)
		created_at = robloxUser.created
		created_at = created_at.replace(tzinfo=pytz.UTC)
		current_time = datetime.datetime.now(pytz.UTC)
		time_diff = current_time - created_at
		roblox_account_age_in_days = time_diff.days

		if 30 > int(roblox_account_age_in_days):
			alerts.append("\n- ⚠️ [This user ROBLOX account age is lesser then the recommended amount 30 days.] ⚠️")

		num_friends = await robloxUser.get_friend_count()

		if num_friends < 30:
			alerts.append("\n* [This user has lesser friends then the recommended amount 30.] ")

		num_groups = len(await robloxUser.get_group_roles())

		if num_friends < 30:
			alerts.append("\n* [This user is in lesser groups then the recommended amount 10.] ")

		duration = now - joined_at
		total_days = duration.total_seconds() / (60 * 60 * 24)
		days = int(round(total_days))
		if days < 30:
			alerts.append("\n* [This user is new to our discord server.] ")

		if alerts:
			alertsValue = "".join(alerts)
		else:
			alertsValue = "\n+ ✅ [This user does not have any alerts. This user has pass our background check.] ✅"

		userDiscordAccountDetails = discord.Embed(title="User Discord Account Details", description=f"", color=discord.Color.blue())
		userDiscordAccountDetails.set_author(name=f"{member.name}#{member.discriminator} | {member.display_name}", icon_url=member.avatar)
		userDiscordAccountDetails.set_thumbnail(url=member.avatar)
		userDiscordAccountDetails.add_field(name="Joined Date", value=member.joined_at.strftime(f"%a, %#d {FDOM} %Y %H:%M:%S GMT"), inline=True)
		userDiscordAccountDetails.add_field(name="Registered Date", value=member.created_at.strftime(f"%a, %#d {FDOM} %Y %H:%M:%S GMT"), inline=True)
		userDiscordAccountDetails.add_field(name=f"User Roles [{len(rolelist)}]", value=f"{rolesBGcheck}", inline=False)
		userDiscordAccountDetails.add_field(name=f"Alerts", value=f"```diff{alertsValue}```", inline=False)

		if robloxUser.description == "":
			robloxDescription = "No description found"
		else:
			robloxDescription = robloxUser.description

		num_followers = await robloxUser.get_follower_count()

		num_followings = await robloxUser.get_following_count()

		api_url = f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={robloxUser.id}&size=48x48&format=Png&isCircular=true'
		response = requests.get(api_url)
		avatar_data = response.json()['data']
		for avatar in avatar_data:
			avatarURL = avatar['imageUrl']
		
		userROBLOXAccountDetails = discord.Embed(title="User ROBLOX Account Details", color=discord.Color.blue())
		userROBLOXAccountDetails.set_author(name=robloxUser.name, url=f"https://www.roblox.com/users/{robloxUser.id}/profile", icon_url=avatarURL)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Age", value=f"{roblox_account_age_in_days} days", inline=False)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Description", value=robloxDescription, inline=False)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Groups", value=num_groups, inline=True)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Friends", value=num_friends, inline=True)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Followers", value=num_followers, inline=True)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Following", value=num_followings, inline=True)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Gamepasses Owned", value=f"Not Programmed.", inline=True)
		userROBLOXAccountDetails.add_field(name=f"ROBLOX Account Badges Owned", value=f"Not Programmed.", inline=True)
		userROBLOXAccountDetails.add_field(name=f"Alerts", value=f"```diff{alertsValue}```", inline=False)

		groups_to_check = [
			32590701, # RGG
			15549981, # ETS
			16195172, # RMP
			15964799, # AAB
			16185446, # OTC
			15549924, # FCO
			15356653, # Main Group
		]

		response = requests.get(f'https://groups.roblox.com/v1/users/{robloxID}/groups/roles')

		regiment_details = []

		group_roles = json.loads(response.content)['data']
		for group_id in groups_to_check:
			user_role = next((role for role in group_roles if role['group']['id'] == group_id), None)
			if user_role is not None:
				regiment_details.append(f"[{user_role['group']['name']} - {user_role['role']['name']}]")

		if regiment_details:
			regiment_details_text = "\n".join(regiment_details)
		else:
			regiment_details_text = "[This user is not in any regiments]"
		
		userRegimentDetails = discord.Embed(title="User Regiment Details", description=f"```{regiment_details_text}```", color=discord.Color.blue())
		userRegimentDetails.set_author(name=robloxUser.name, url=f"https://www.roblox.com/users/{robloxUser.id}/profile", icon_url=avatarURL)
		userRegimentDetails.add_field(name=f"Alerts", value=f"```diff{alertsValue}```", inline=False)

		embed_list = [userDiscordAccountDetails, userROBLOXAccountDetails, userRegimentDetails]

		await backgroundCheck.edit(embed=userDiscordAccountDetails.set_footer(text=f"Viewing Page 1 / {len(embed_list)}", icon_url=""))

		async def update_bgcheck_message(message, embed_index):
			embed = embed_list[embed_index]
			embed.set_footer(text=f"Viewing Page {embed_index + 1} / {len(embed_list)}", icon_url="")
			await message.edit(embed=embed)

		current_embed_index = 0

		await backgroundCheck.add_reaction('⬅️')
		await backgroundCheck.add_reaction('➡️')
		await backgroundCheck.add_reaction('🗑️')

		emoji_to_func = {
			'⬅️': lambda: None,  # Do nothing for the left arrow
			'➡️': lambda: update_bgcheck_message(backgroundCheck, 1),  # Update to embed 2 for right arrow
			'🗑️': lambda: backgroundCheck.delete()  # Delete the message for the bin emoji
		}

		@bot.event
		async def on_reaction_add(reaction, user):
			nonlocal current_embed_index

			if user != ctx.author or reaction.message.channel != backgroundCheck.channel:
				return

			emoji = str(reaction.emoji)
			func = emoji_to_func.get(emoji)

			if func:
				func()

				# Remove the reaction
				await reaction.remove(user)

				# Update the current embed index based on the right arrow or left arrow
				if emoji == '➡️':
					current_embed_index = min(current_embed_index + 1, len(embed_list) - 1)
					await update_bgcheck_message(backgroundCheck, current_embed_index)
				elif emoji == '⬅️':
					current_embed_index = max(current_embed_index - 1, 0)
					await update_bgcheck_message(backgroundCheck, current_embed_index)
				elif emoji == '🗑️':
					await backgroundCheck.delete()

	@commands.hybrid_command(
		name="commands",
		description="No Description Specified.",
		extras={"category": "Miscellaneous", "levelPermissionNeeded": 0},
		with_app_command=True,
		enabled=True
	)
	async def commands(self, ctx: commands.Context):
		bot = self.bot
		has_command_categories = False

		categories = []
		commands = []

		for command in bot.walk_commands():
				has_command_categories = True

				try:
					command.category = command.extras['category']
				except:
					command.category = 'Miscellaneous'

				if command.extras.get('legacy') is True:
					continue

				if isinstance(command, discord.ext.commands.core.Command):
					if command.hidden:
						continue
					if command.parent is not None:
						if isinstance(command.parent,
									discord.ext.commands.core.Group) and not command.parent.name == "jishaku" and not command.parent.name == "jsk":
							if command.parent.name not in ['voice']:
								command.full_name = f"{command.full_parent_name} {command.name}"
							else:
								continue
						else:
							continue
					else:
						command.full_name = f"{command.name}"

				if isinstance(command, discord.ext.commands.core.Group):
					continue

				if command.category not in categories:
					categories.append(command.category)
					commands.append(command)
				else:
					commands.append(command)

		commandCategories = set()

		for category in categories:
			commandCategories.add(category)

		if has_command_categories:
			selectCommandCategory = discord.Embed(title="Commands List", description="Select the command category you wish to view", color=discord.Color.dark_blue())
			selectCommandCategory.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

			options = []
			for category in commandCategories:
				options.append(
					discord.SelectOption(
						label=category,
						description=f"View commands for the {category} category",
						value=category,
					)
				)

			view = CustomCommandsMenu(ctx.author.id, options, commands)

			await ctx.send(embed=selectCommandCategory, view=view)

		if not has_command_categories:
			noCommandsCategoriesFound = discord.Embed(title="Warning - No Command Categories", description=f"We were unable to find any command categories.", color = discord.Color.dark_gold())
			noCommandsCategoriesFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=noCommandsCategoriesFound)
			return

async def setup(bot):
	await bot.add_cog(Miscellaneous(bot))
