import discord
from discord.ext import commands
from discord import app_commands

from utils.utils import get_admin_level
from utils.utils import optionsDict
import datetime
from menus import CustomActionsMenu, ReportAbuse, UnbanAll, RuleSelectionMenu, CustomModerateMenu
import asyncio
from utils.utils import update_member
from utils.utils import client, TRELLO_API_KEY, TRELLO_API_TOKEN
import requests

class Moderation(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.hybrid_group(
		name='actions',
		extras={"category": "Moderation", "levelPermissionNeeded": 0},
		with_app_command=True
	)
	async def actions(self, ctx):
		pass

	@actions.command(
		name='delete',
		description='Delete a certain action id',
		usage="/actions delete {action_id}",
		extras={"category": "Moderation", "levelPermissionNeeded": 3},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(action_id="The ID of the action you wish to delete")
	async def actions_delete(self, ctx: commands.Context, action_id):
		bot = self.bot
		try:
			id = int(action_id.replace(' ', ''))
		except:
			return await ctx.send(ctx, '`id` is not a valid ID.')

		selected_item = None
		selected_items = []
		item_index = 0

		async for item in bot.actions.db.find({'actions': {'$elemMatch': {'id': id}}}):
			for index, _item in enumerate(item['actions']):
				if _item['id'] == id:
					selected_item = _item
					selected_items.append(_item)
					parent_item = item
					item_index = index
					break

		if selected_item is None:
			actionDoesNotExist = discord.Embed(title = "Warning - Action Not Found", description=f"The action with action ID {action_id} was not found.", color = discord.Color.dark_gold())
			actionDoesNotExist.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=actionDoesNotExist)

		if len(selected_items) > 1:
				return await ctx.send('There is more than one punishment associated with this ID. Please contact Alfie as soon as possible. I have cancelled the removal of this warning since it is unsafe to continue.')

		parent_item['actions'].remove(selected_item)
		await bot.actions.update_by_id(parent_item)

		action_reason = selected_item['Reason']
		if isinstance(action_reason, list):
			actionReason = []
			for rule in sorted(action_reason, key=int):
				rule_label = f"Rule {int(rule)}"
				actionReason.append(rule_label)
			action_reason = ", ".join(actionReason)

		actionDeleted = discord.Embed(
				title=f"Action Deleted",
				description=f"**ACTION ID:** #{selected_item['id']}\n**ACTION TYPE:** {selected_item['Type']}\n**ACTION DATE:** {selected_item['Date']}\n**ACTION BY:** <@{selected_item['Moderator']}>\n**ACTION INFO:** {action_reason}",
				color=discord.Color.dark_blue(),
			)
		actionDeleted.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
		await ctx.send(embed=actionDeleted)

	@actions.command(
		name='clear',
		description='Clear all actions from a member',
		usage="/actions clear {member}",
		extras={"category": "Moderation", "levelPermissionNeeded": 5},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(member="The member you wish to clear their actions")
	async def actions_clear(self, ctx: commands.Context, member: discord.User):
		bot = self.bot
		dataset = await bot.actions.find_by_id(member.id)

		if dataset:
			RESULTS = []
			
			dataset['actions'][0]['name'] = member.id
			RESULTS.append(dataset['actions'])

			result_var = None

			for result in RESULTS:
				if result[0]['name'] == RESULTS[0][0]['name']:
					result_var = RESULTS[0]

			result = result_var

			supportLogsEmbed = discord.Embed(title="Warnings Cleared", description=f"Username Of Moderator : {ctx.message.author.mention}\nUser Cleared : {member.mention}", color=discord.Color.blue(), timestamp=datetime.datetime.now())
			supportLogs = bot.get_channel(1069671496244539443)

			for action in result:
				if len(supportLogsEmbed.fields) <= 2:
						supportLogsEmbed.add_field(
							name=f"\n",
							value=f"**ACTION ID:** {action['id']}\n**ACTION TYPE : {action['Type']}**\nACTION DATE : **{action['Date']}**\nACTION BY : <@{action['Moderator']}>\nACTION INFO: {action['Reason']}",
							inline=False
						)
				else:
					supportLogsEmbed.add_field(
						name=f"\n",
						value=f"**ACTION ID:** {action['id']}\n**ACTION TYPE : {action['Type']}**\nACTION DATE : **{action['Date']}**\nACTION BY : <@{action['Moderator']}>\nACTION INFO : {action['Reason']}",
						inline=False
					)
			await supportLogs.send(embed=supportLogsEmbed)

			await bot.actions.delete_by_id(member.id)

			clearActionHistory = discord.Embed(
				title=f"Actions Cleared",
				description=f"Cleared all actions for user {member.mention}",
				color=discord.Color.dark_blue(),
			)
			clearActionHistory.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
			await ctx.send(embed=clearActionHistory)
		
		else:
			noActions = discord.Embed(title="Warning - No Warnings Found", description="There are no warnings found on this user", color=discord.Color.dark_gold())
			noActions.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
			await ctx.send(embed=noActions)

	@actions.command(
		name='view',
		description='Views a member actions or a certain action id',
		usage="/actions view {member} {action_id}",
		extras={"category": "Moderation", "levelPermissionNeeded": 2},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(member="The member you wish to view the action log")
	@app_commands.describe(action_id="The ID of the action you wish to view in detail")
	async def actions_view(self, ctx: commands.Context, member: discord.User=None, action_id: int=None):
		bot = self.bot
		if member == None and action_id == None:
			notFound = discord.Embed(title="Warning - Invalid Arguments", description="The member you are trying to view does not exist", color=discord.Color.dark_gold())
			notFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=notFound)
		if member:
			dataset = await bot.actions.find_by_id(member.id)
			
			if dataset:
				actionTypes = []

				for action in dataset['actions']:
					if action['Type'] not in actionTypes:
						actionTypes.append(action['Type'])

				options = [
					discord.SelectOption(
						label="All",
						description="View all action history",
						value="all",
					)
				]

				for action_type in actionTypes:
					options.append(
						discord.SelectOption(
							label=action_type.title(),
							description=f"View {action_type.title()} action history",
							value=action_type.lower(),
						)
					)

				try:
					if member.nick:
						memberNickname = member.nick
					else:
						memberNickname = member.name
				except:
					memberNickname = member.name
				selectActionType = discord.Embed(title=f"Viewing Action History For {memberNickname}", description="Select the action type you wish to view", color=discord.Color.dark_blue())
				selectActionType.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				return await ctx.send(embed=selectActionType, view=CustomActionsMenu(ctx.author.id, options, member, bot))
			else:
				noActions = discord.Embed(title="Warning - No actions found", description="The member you are trying to view has no actions record found.", color=discord.Color.dark_gold())
				noActions.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
				return await ctx.send(embed=noActions)
		if action_id:
			action = None
			user = None
			for item in await bot.actions.get_all():
				for each in item["actions"]:
					if each["id"] == action_id:
						action = each
						user = item["_id"]

			if action is None:
				noAction = discord.Embed(title="Warning - No action found", description="The ID you are trying to view has no action record found.", color=discord.Color.dark_gold())
				noAction.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
				return await ctx.send(embed=noAction)

			try:
				guildName = bot.get_guild(action['Server']).name
			except:
				guildName = "Unknown Server"

			action_reason = action['Reason']
			if isinstance(action_reason, list):
				reason = []
				for rule in sorted(action_reason, key=int):
					rule_label = f"Rule {int(rule)}"
					rule_detail = optionsDict.get(int(rule))["description"]
					if rule_detail:
						reason.append(f"{rule_label}. {rule_detail}")

				evidence = []
				for each in action['Evidence']:
					evidence.append(each)

				moderationReason = "\n".join(reason)
				evidence = "\n".join(evidence)
				action_reason = f"\n\nRules Violated:\n```{moderationReason}```\nDuration: {action['Duration']}\n\nEvidence:\n```{evidence}```"
			
			viewActionInDetail = discord.Embed(
					title=f"Viewing Action #{action['id']}",
					description=f"**ACTION ID:** #{action['id']}\n**MODERATED USER:** <@{user}>\n**ACTION TYPE:** {action['Type']}\n**ACTION DATE:** {action['Date']}\n**ACTION BY:** <@{action['Moderator']}>\n**ACTION INFO:** {action_reason}\n**SERVER:** {guildName}",
					color=discord.Color.dark_blue(),
				)
			viewActionInDetail.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
			await ctx.send(embed=viewActionInDetail)

	@commands.hybrid_command(
		name="warn",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 2},
		with_app_command=True,
		enabled=True,
	)
	@app_commands.describe(member="Please mention the user you wish to warn")
	@app_commands.describe(warning="Please enter the warning you wish to issue")
	async def warn(self, ctx: commands.Context, member: discord.User, *, warning):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)
		memberWarning = int(await get_admin_level(bot, ctx.guild, member.id))
		if memberWarning >= userAdminLevel:
			sameAdminLevel = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This member you are trying to warn has the same of higher admin level than you.", color = discord.Color.dark_gold())
			sameAdminLevel.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=sameAdminLevel)

		warningsCount = 0
		user = await bot.actions.find_by_id(member.id)
		if user is None:
			warningsCount += 1
		else:
			for warningItem in user['actions']:
				if warningItem['Type'] == "Warn":
					warningsCount += 1
			warningsCount += 1

		actionID = 0
		for item in await bot.actions.get_all():
			for action in item["actions"]:
				actionID += 1
		actionID += 1

		default_action_item = {
			'_id': member.id,
			'actions': [{
				'id': actionID,
				"Type": "Warn",
				"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
				"Moderator": ctx.author.id,
				"Reason": warning,
				"Server": ctx.guild.id
			}]
		}

		singular_action_item = {
			'id': actionID,
				"Type": "Warn",
				"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
				"Moderator": ctx.author.id,
				"Reason": warning,
				"Server": ctx.guild.id
		}

		if not await bot.actions.find_by_id(member.id):
			await bot.actions.insert(default_action_item)
		else:
			dataset = await bot.actions.find_by_id(member.id)
			dataset['actions'].append(singular_action_item)
			await bot.actions.update_by_id(dataset)

		warnEmbed = discord.Embed(title="User Warned", description=f"Successfully warned user {member.mention} with reason : {warning}.\n\nUser is currently on {warningsCount} warnings.", color=discord.Color.dark_blue())
		warnEmbed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		DM_warn = discord.Embed(title="Warn Notice", description=f"You have received a warn in {ctx.guild.name}.\n\nWarning : {warning}", color=discord.Color.dark_gold())
		DM_warn.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		await ctx.send(embed=warnEmbed)

		try:
			await member.send(embed=DM_warn)
		except:
			pass

	@commands.hybrid_command(
		name="kick",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 4},
		with_app_command=True,
		enabled=True,
	)
	@app_commands.describe(member="The user you wish to kick")
	@app_commands.describe(reason="The reason you wish to kick the user")
	async def kick(self, ctx: commands.Context, member: discord.Member, *, reason):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)
		memberKicking = int(await get_admin_level(bot, ctx.guild, member.id))
		if memberKicking >= userAdminLevel:
			sameAdminLevel = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This member you are trying to kick has the same of higher admin level than you.", color = discord.Color.dark_gold())
			sameAdminLevel.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=sameAdminLevel)
		
		actionID = 0
		for item in await bot.actions.get_all():
			for action in item["actions"]:
				actionID += 1
		actionID += 1

		default_action_item = {
				'_id': member.id,
				'actions': [{
					'id': actionID,
					"Type": "Kick",
					"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": ctx.author.id,
					"Reason": reason,
					"Server": ctx.guild.id
				}]
			}

		singular_action_item = {
				'id': actionID,
					"Type": "Kick",
					"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": ctx.author.id,
					"Reason": reason,
					"Server": ctx.guild.id
			}

		if not await bot.actions.find_by_id(member.id):
			await bot.actions.insert(default_action_item)
		else:
			dataset = await bot.actions.find_by_id(member.id)
			dataset['actions'].append(singular_action_item)
			await bot.actions.update_by_id(dataset)

		DM_kick = discord.Embed(title="Kick Notice", description=f"You have been kicked from {ctx.guild.name} server.\n\nReason : {reason}", color=discord.Color.dark_gold())
		DM_kick.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)

		channel = bot.get_channel(1069671496244539443)
		embed = discord.Embed(title="User Kicked", description=f"Succesfully kicked user {member.mention} with reason : {reason}", color=discord.Color.dark_blue())
		embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
		await ctx.send(embed=embed)
		embed = discord.Embed(title="User Kicked", description=f"Username Of Moderator : {ctx.message.author.mention}\nUser Kicked : {member.mention} | {member.display_name} | {member.name}#{member.discriminator}\nReason : {reason}", color=0x6fff3e, timestamp=datetime.datetime.now())
		await channel.send(embed=embed)

		try:
			await member.send(embed=DM_kick)
		except:
			pass

		await member.kick(reason=f"{reason}. - {ctx.author.nick}")

	@commands.hybrid_command(
		name="ban",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 4},
		with_app_command=True,
		enabled=True,
	)
	@app_commands.describe(user_id="The user you wish to ban")
	@app_commands.describe(reason="The reason you wish to ban the user")
	async def ban(self, ctx: commands.Context, user_id: discord.User, *, reason: str):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)
		try:
			memberBanning = int(await get_admin_level(bot, ctx.guild, user_id.id))
			if memberBanning >= userAdminLevel:
				sameAdminLevel = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This member you are trying to ban has the same of higher admin level than you.", color = discord.Color.dark_gold())
				sameAdminLevel.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				return await ctx.send(embed=sameAdminLevel)
		except:
			pass

		banConfirmation = discord.Embed(title="User Banned", description=f"Succesfully banned user {user_id.mention} with reason : {reason} from British Army and all of it's associated servers.", color=discord.Color.dark_blue())
		banConfirmation.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		await ctx.send(embed=banConfirmation)

		banNotice = discord.Embed(title="Ban Notice", description=f"You have been permenantly banned in British Army and all of it's associated servers.\n\nBan Origin : {ctx.guild.name}\n\nReason : {reason}\n\nAppeal here : https://forms.gle/3N2sNsGAgZzwSrLAA", color=discord.Color.dark_gold())
		banNotice.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		try:
			await user_id.send(embed=banNotice)
		except:
			pass

		for guild in bot.guilds:
			await guild.ban(user_id, reason=f"{reason}. - {ctx.author.nick} | Banned in {ctx.guild.name}")

		moderationLogs = bot.get_channel(1069671496244539443)
		banLog = discord.Embed(title="User Banned", description=f"Username Of Moderator : {ctx.author.mention}\nUser PBanned : {user_id.mention} | {user_id.display_name} | {user_id.name}#{user_id.discriminator}\nReason : {reason}", color=0xFF3A10, timestamp=datetime.datetime.now())
		await moderationLogs.send(embed=banLog)

		actionID = sum(len(item["actions"]) for item in await bot.actions.get_all()) + 1

		singular_action_item = {
			'id': actionID,
			"Type": "Ban",
			"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
			"Moderator": ctx.author.id,
			"Reason": reason,
			"Server": ctx.guild.id
		}

		default_action_item = {
			'_id': user_id.id,
			'actions': [singular_action_item]
		}

		if not await bot.actions.find_by_id(user_id.id):
			await bot.actions.insert(default_action_item)
		else:
			dataset = await bot.actions.find_by_id(user_id.id)
			dataset['actions'].append(singular_action_item)
			await bot.actions.update_by_id(dataset)

		dataset = await bot.roblox.find_by_id(user_id.id)

		if dataset:
			default_action_item = {
				'_id': user_id.id,
				'roblox': dataset['roblox'],
				'banned': True,
				'suspended': dataset['suspended']
			}

			await bot.roblox.update(default_action_item)

	@commands.hybrid_command(
		name="mute",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 3},
		with_app_command=True,
		enabled=True,
	)
	@app_commands.describe(member="The user you wish to mute")
	@app_commands.describe(duration="The duration you wish to mute the user for")
	@app_commands.describe(reason="The reason you wish to mute the user")
	async def mute(self, ctx: commands.Context, member: discord.Member,  duration, *, reason):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)
		memberMuting = int(await get_admin_level(bot, ctx.guild, member.id))
		if memberMuting >= userAdminLevel:
			sameAdminLevel = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This member you are trying to mute has the same of higher admin level than you.", color = discord.Color.dark_gold())
			sameAdminLevel.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=sameAdminLevel)
			return
		
		if member.is_timed_out():
			alreadyMuted = discord.Embed(title = "Warning - User Muted", description=f"This member you are trying to mute has been muted already.", color = discord.Color.dark_gold())
			alreadyMuted.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=alreadyMuted)
			return
		else:
			pass

		actionID = 0
		for item in await bot.actions.get_all():
			for action in item["actions"]:
				actionID += 1
		actionID += 1

		default_action_item = {
				'_id': member.id,
				'actions': [{
					'id': actionID,
					"Type": "Mute",
					"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": ctx.author.id,
					"Reason": reason,
					"Server": ctx.guild.id
				}]
			}

		singular_action_item = {
				'id': actionID,
					"Type": "Mute",
					"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": ctx.author.id,
					"Reason": reason,
					"Server": ctx.guild.id
			}

		try:
			timeoutUnit = duration[len(duration)-1]
			timeoutLength = int(duration[:-1])
			
			if timeoutUnit.lower() == "d":
				timeoutDuration = datetime.timedelta(days=timeoutLength, seconds=0, microseconds=0)
				if timeoutLength > 7 and not userAdminLevel >= 5:
					invalidArguments = discord.Embed(title = "Warning - Invalid Arguments", description=f"The maximum duration you can mute for is `7 days`", color = discord.Color.dark_gold())
					invalidArguments.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					await ctx.send(embed=invalidArguments)
					return
				elif timeoutLength > 28:
					invalidArguments = discord.Embed(title = "Warning - Invalid Arguments", description=f"The maximum duration you can mute for is `28 days`", color = discord.Color.dark_gold())
					invalidArguments.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					await ctx.send(embed=invalidArguments)
					return
			elif timeoutUnit.lower() == "h":
				timeoutDuration = datetime.timedelta(days=0, hours=timeoutLength, seconds=0, microseconds=0)
			elif timeoutUnit.lower() == "m":
				timeoutDuration = datetime.timedelta(days=0, hours=0, minutes=timeoutLength, microseconds=0)

			if not await bot.actions.find_by_id(member.id):
				await bot.actions.insert(default_action_item)
			else:
				dataset = await bot.actions.find_by_id(member.id)
				dataset['actions'].append(singular_action_item)
				await bot.actions.update_by_id(dataset)

			channel = bot.get_channel(1069671496244539443)

			muteEmbed = discord.Embed(title="User Muted", description=f"Succesfully muted user {member.mention} for {duration} with reason : {reason}.", color=discord.Color.dark_blue())
			muteEmbed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=muteEmbed)

			embed = discord.Embed(title="User Muted", description=f"Username Of Moderator : {ctx.message.author.mention}\nUser Muted : {member.mention}\nDuration : {duration}\nReason : {reason}", color=0x6fff3e, timestamp=datetime.datetime.now())
			await channel.send(embed=embed)

			DM_mute = discord.Embed(title="Mute Notice", description=f"You have been muted from {ctx.guild.name} server.\n\nDuration : {duration}\n\nReason : {reason}\n\nIf you feel that you might have muted incorrectly, please press the button below.\n**Please note that making false reports will result in an extended mute duration or worse banned from the server permanently, DO NOT USE IT TO APPEAL FOR YOUR MUTES**", color=discord.Color.dark_gold())
			DM_mute.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)

			await member.timeout(timeoutDuration, reason=f"{reason}. - {ctx.author.nick}")

			view = ReportAbuse(member.id)
			await member.send(embed=DM_mute, view=view)
			timeout = await view.wait()
			if timeout:
				return

			if view.value is True:
				category = discord.utils.get(ctx.guild.categories, id=1091254812819066891)

				supportTeam = ctx.guild.get_role(1069672694175506463)

				ticketCreator = member

				ticket_number = 1
				ticketType = "report"

				for channel in category.channels:
					if isinstance(channel, discord.TextChannel):
						if channel.name.split('-')[0] == ticketType:
							ticket_number += 1

				name = f"{ticketType}-{ticket_number}"

				overwrites = {
							ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
							ticketCreator: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
							supportTeam: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
						}
				channel = await ctx.guild.create_text_channel(name = name, topic=f"otherReport:{ticketCreator.id}", overwrites = overwrites, category=category)

				welcomeEmbed = discord.Embed(title="REPORT TICKET", description=f"**Unfair Mute Report Ticket**\n\nAll mods, please do not intervene into this ticket and escalate it to an administrator immediately, failure to do so would result in a removal.\n\nModerator Reported: {ctx.author.nick}\nMute Duration: {duration}\nMute Reason: {reason}", color=discord.Color.dark_blue())
				welcomeEmbed.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)
				message = await channel.send(f"{ticketCreator.mention}, {supportTeam.mention}", embed=welcomeEmbed)

				await asyncio.sleep(1)
				
				def check(m):
					if m.author.bot:
						return False
					return supportTeam in m.author.roles and m.channel == channel

				response = await ctx.bot.wait_for("message", check=check)
				
				supportArrived = discord.Embed(
					title="**Support has arrived!**",
					description=f"{response.author.mention} will now be assisting with your report.",
					color=discord.Color.dark_blue(),
				)
				supportArrived.set_author(name=f"{response.author.name}", icon_url=response.author.avatar)
				await channel.send(ticketCreator.mention, embed=supportArrived)

				claimedMod = response.author
				await channel.edit(topic=f"{channel.topic}-{claimedMod.id}")
		except:
			invalidArguments = discord.Embed(title = "Warning - Invalid Arguments", description=f"Invalid mute duration", color = discord.Color.dark_gold())
			invalidArguments.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=invalidArguments)

	@commands.hybrid_command(
		name="suspend",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 4},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(member="The user you wish to suspend")
	@app_commands.describe(reason="The reason you wish to suspend the user")
	async def suspend(self, ctx: commands.Context, member: discord.User, *, reason: str):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)
		memberSuspending = int(await get_admin_level(bot, ctx.guild, member.id))
		if memberSuspending >= userAdminLevel:
			sameAdminLevel = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This member you are trying to suspend has the same of higher admin level than you.", color = discord.Color.dark_gold())
			sameAdminLevel.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=sameAdminLevel)
			return
		
		actionID = 0
		for item in await bot.actions.get_all():
			for action in item["actions"]:
				actionID += 1
		actionID += 1

		default_action_item = {
				'_id': member.id,
				'actions': {
					'id': actionID,
					"Type": "Suspend",
					"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": ctx.author.id,
					"Reason": reason,
					"Server": ctx.guild.id
				}
			}

		singular_action_item = {
				'id': actionID,
					"Type": "Suspend",
					"Date": ctx.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": ctx.author.id,
					"Reason": reason,
					"Server": ctx.guild.id
			}

		if not await bot.actions.find_by_id(member.id):
			await bot.actions.insert(default_action_item)
		else:
			dataset = await bot.actions.find_by_id(member.id)
			dataset['actions'].append(singular_action_item)
			await bot.actions.update_by_id(dataset)

		DM_suspend = discord.Embed(title="Suspension Notice", description=f"You have been suspended in British Army and all of it's associated servers.\n\nSuspension Origin : {ctx.guild.name}\n\nReason : {reason}", color=discord.Color.dark_gold())
		DM_suspend.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		embed = discord.Embed(title="User Suspended", description=f"Succesfully suspended user {member.mention} with reason : {reason} from British Army and all of it's associated servers.", color=discord.Color.dark_blue())
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		await ctx.send(embed=embed)


		embed = discord.Embed(title="User Suspended", description=f"Username Of Moderator : {ctx.message.author.mention}\nUser Suspended : {member.mention} | {member.display_name} | {member.name}#{member.discriminator}\nReason : {reason}", color=0xFF3A10, timestamp=datetime.datetime.now())
		supportLogs = bot.get_channel(1069671496244539443)
		await supportLogs.send(embed=embed)

		dataset = await bot.roblox.find_by_id(member.id)

		if dataset:
			default_action_item = {
				'_id': member.id,
				'roblox': dataset['roblox'],
				'banned': dataset['banned'],
				'suspended': True,
			}

			await bot.roblox.update(default_action_item)
			for guild in bot.guilds:
				await update_member(bot, member, guild)

		try:
			await member.send(embed=DM_suspend)
		except:
			pass

	@commands.hybrid_command(
		name="unsuspend",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 4},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(user_id="The user you wish to unsuspend")
	async def unsuspend(self, ctx: commands.Context, user_id: discord.User):
		bot = self.bot
		dataset = await bot.roblox.find_by_id(user_id.id)

		if dataset:
			if dataset['suspended'] == False:
				userNotSuspended = discord.Embed(title = "Warning - No Suspension Records Found", description=f"This user isn't suspended", color = discord.Color.dark_gold())
				userNotSuspended.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				await ctx.send(embed=userNotSuspended)
				return
			
			DM_unsuspend = discord.Embed(title="Unsuspension Notice", description=f"You have been unsuspended in British Army and all of it's associated servers.", color=discord.Color.dark_gold())
			DM_unsuspend.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

			embed = discord.Embed(title="User Unsuspended", description=f"Succesfully unsuspended user {user_id.mention} from British Army and all of it's associated servers.", color=discord.Color.dark_blue())
			embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=embed)

			embed = discord.Embed(title="User Unsuspended", description=f"Username Of Moderator : {ctx.message.author.mention}\nUser Unsuspended : {user_id.mention} | {user_id.display_name} | {user_id.name}#{user_id.discriminator}", color=discord.Color.blue(), timestamp=datetime.datetime.now())
			supportLogs = bot.get_channel(1069671496244539443)
			await supportLogs.send(embed=embed)

			try:
				await user_id.send(embed=DM_unsuspend)
			except:
				pass

			default_action_item = {
				'_id': user_id.id,
				'roblox': dataset['roblox'],
				'banned': dataset['banned'],
				'suspended': False
			}

			await bot.roblox.update(default_action_item)
			for guild in bot.guilds:
				await update_member(bot, user_id, guild)

	@commands.command(
		name="robloxban",
		description="robloxban",
		extras={"category": "Moderation", "levelPermissionNeeded": 6},
		with_app_command=False,
		enabled=True
	)
	async def robloxban(self, ctx: commands.Context, robloxUsername):
		bot = self.bot
		try:
			user = await client.get_user_by_username(robloxUsername, expand=True)
			
			dataset = await bot.roblox.find_by_id(ctx.author.id)
			if dataset:
				robloxUser = await client.get_user(dataset['roblox'])

			card_name = f"{user.id}:{robloxUser.id}"

			url = f'https://api.trello.com/1/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}&idList=63ebf6eec879232baafd4209&name={card_name}'
			response = requests.post(url)

			if response.status_code == 200:
				successfulGameBan = discord.Embed(title="User Banned", description=f"Succesfully banned user {robloxUsername} from the game.", color=discord.Color.dark_blue())
				successfulGameBan.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				await ctx.send(embed=successfulGameBan)
			else:
				unsuccessfulGameBan = discord.Embed(title="Unsuccessful Game Ban", description=f"The ROBLOX account username you have entered does not exist.", color=0xd30013)
				successfulGameBan.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				await ctx.send(embed=unsuccessfulGameBan)
		except:
			unsuccessfulGameBan = discord.Embed(title="Unsuccessful Game Ban", description=f"The ROBLOX account username you have entered does not exist.", color=0xd30013)
			unsuccessfulGameBan.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=unsuccessfulGameBan)

	@commands.hybrid_command(
		name="unban",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 0},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(user_id="The user you wish to unban")
	@app_commands.describe(all="Unbans everyone in the server")
	async def unban(self, ctx: commands.Context, user_id: discord.User=None, all: bool=False):
		bot = self.bot
		if all == True:
			adminLevelRequired = 6
			userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

			if not userAdminLevel >= adminLevelRequired:
				insufficientPermissions = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This `all` option of this command is limited to the admin level **{adminLevelRequired}**!", color = discord.Color.dark_gold())
				insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				return await ctx.send(embed=insufficientPermissions)
			
			totalBans = 0
			async for ban_entry in ctx.guild.bans():
				totalBans += 1

			unbanConfirm = discord.Embed(title="Unban All", description=f"Are you sure you want to unban {totalBans} members?", color=discord.Color.dark_blue())
			unbanConfirm.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=unbanConfirm, view=UnbanAll(ctx.author.id, self.bot)) 

		elif user_id != None:
			adminLevelRequired = 5
			userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

			if not userAdminLevel >= adminLevelRequired:
				insufficientPermissions = discord.Embed(title = "Warning - Insufficient Permissions", description=f"The `user_id` option of this command is limited to the admin level **{adminLevelRequired}**!", color = discord.Color.dark_gold())
				insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				return await ctx.send(embed=insufficientPermissions)

			embed = discord.Embed(title="User Unbanned", description=f"Succesfully unbanned user {user_id.mention} from British Army and all of it's associated servers.", color=discord.Color.dark_blue())
			embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=embed)

			embed = discord.Embed(title="User Unbanned", description=f"Username Of Moderator : {ctx.message.author.mention}\nUser Unbanned : {user_id.mention} | {user_id.display_name} | {user_id.name}#{user_id.discriminator}", color=discord.Color.blue(), timestamp=datetime.datetime.now())
			supportLogs = bot.get_channel(1069671496244539443)
			await supportLogs.send(embed=embed)

			dataset = await bot.roblox.find_by_id(user_id.id)

			if dataset:
				default_action_item = {
					'_id': user_id.id,
					'roblox': dataset['roblox'],
					'banned': False,
					'suspended': dataset['suspended']
				}

				await bot.roblox.update(default_action_item)

			for guild in bot.guilds:
				try:
					await guild.unban(user_id)
				except:
					pass
		else:
			embed = discord.Embed(title="User Unbanned", description=f"Succesfully unbanned user <@> from British Army and all of it's associated servers.", color=discord.Color.dark_blue())
			embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=embed)

	@commands.hybrid_command(
		name="moderate",
		description="No Description Specified.",
		extras={"category": "Moderation", "levelPermissionNeeded": 2, "ephemeral": True},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(member="The user you wish to moderate")
	async def moderate(self, ctx: commands.Context, member: discord.User):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)
		
		memberModerating = int(await get_admin_level(bot, ctx.guild, member.id))
		if memberModerating >= userAdminLevel:
			sameAdminLevel = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This member you are trying to moderate has the same of higher admin level than you.", color = discord.Color.dark_gold())
			sameAdminLevel.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=sameAdminLevel, ephemeral=True)

		if userAdminLevel >= 4:
			options = [
				discord.SelectOption(label="Watchlist", value="Watchlist", description="Temporarily adds the user to our watchlist where they will be heavily monitored"),
				discord.SelectOption(label="Timeout", value="Timeout", description="Timeout / mute the user for a set amount of time based on the rules broken"),
				discord.SelectOption(label="Suspension", value="Suspension", description="Temporarily suspends the user from the server"),
				discord.SelectOption(label="Ban", value="Ban", description="Temporarily bans the user from the server"),
			]

			view = CustomModerateMenu(member, options, bot)

			selectAction = discord.Embed(title="Moderate User", description="Please select the type of moderation action you wish to take against this user.", color=discord.Color.dark_blue())
			selectAction.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=selectAction, view=view, ephemeral=True)
		else:
			options = []
			for index, (rule, description) in enumerate(optionsDict.items(), start=1):
				rule_info = optionsDict.get(rule)
				option = discord.SelectOption(label=f"Rule {rule}", value=index, description=rule_info["description"])
				options.append(option)

			view = RuleSelectionMenu(member, options, bot)

			selectRule = discord.Embed(title="Moderate User", description="Please select the rule(s) the user has violated", color=discord.Color.dark_blue())
			selectRule.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=selectRule, view=view, ephemeral=True)

async def setup(bot):
	await bot.add_cog(Moderation(bot))
