import discord
from zuid import ZUID
import requests
import re
import time

owners = [
	1131274836681949254, # Alfie
	684687856848994304 # Mat
]

TRELLO_API_KEY = '001e9671f82ffc8e75fb99bc9fadf81f'
TRELLO_API_TOKEN = 'ATTA4b064783acf2d724e6cae6b86c324eb28ed43bf00bb00b57b5f6f4a802f5bf0b05BCB044'

from roblox import Client
client = Client()

colour_roles = ['Cyan', 'Lime', 'Bubblegum', 'Purple', 'Lemon', 'Scarlet', 'Orange', 'Electric', 'Mango']
timezoneRoles = ["GMT", "EST", "AEST"]

optionsDict = {
	1: {
		"description": "Respect everyone",
		"duration": 5
	},
	2: {
		"description": "Keep Voice Channels clean and avoid mic spam",
		"duration": 3
	},
	3: {
		"description": "Spamming and trolling are prohibited",
		"duration": 5
	},
	4: {
		"description": "Advertising and Invites are not permitted",
		"duration": 5
	},
	5: {
		"description": "No excessive profanity",
		"duration": 5
	},
	6: {
		"description": "Do not encourage rule violations",
		"duration": 7
	},
	7: {
		"description": "Not-Safe-For-Work is prohibited",
		"duration": 9
	},
	8: {
		"description": "Adult content is prohibited",
		"duration": 9
	},
	9: {
		"description": "No Doxing, IP Logging, or Phishing",
		"duration": 7
	},
	10: {
		"description": "No Debating or destructive criticism",
		"duration": 4
	},
}

error_gen = ZUID(prefix="", length=4)

def is_user_in_group_with_rank(groups_data, group_id, rank):
	for group in groups_data:
		if int(group['group']['id']) == int(group_id) and int(group['role']['rank']) == int(rank):
			return True

	return False

async def get_valid_ranks(group_id):
	group = await client.get_group(group_id)
	rank_info = await group.get_roles()

	valid_ranks = []

	for rank in rank_info:
		if rank.rank >= 1 and rank.rank <= 255:
			valid_ranks.append(rank.rank)

	return valid_ranks

def calculateShiftTimes(dataset):
		if dataset["AFKStartTime"] != 0:
			shiftTime = (time.time() - dataset["ShiftStartTime"]) - (dataset["PreviousAFKTime"] + (time.time() - dataset["AFKStartTime"]))
		else:
			shiftTime = (time.time() - dataset["ShiftStartTime"]) - dataset["PreviousAFKTime"]
		minutes, seconds = divmod(shiftTime, 60)
		if minutes >= 60:
			hours, minutes = divmod(minutes, 60)
			shiftTime = f"{hours:.0f} hour(s) {minutes:.0f} minute(s)"
		else:
			shiftTime = f"{minutes:.0f} minute(s)"

		if dataset["AFKStartTime"] != 0:
			AFKTime = (time.time() - dataset["AFKStartTime"]) + dataset["PreviousAFKTime"]
		else:
			AFKTime = dataset["PreviousAFKTime"]
		minutes, seconds = divmod(AFKTime, 60)
		if minutes >= 60:
			hours, minutes = divmod(minutes, 60)
			AFKTime = f"{hours:.0f} hour(s) {minutes:.0f} minute(s)"
		else:
			AFKTime = f"{minutes:.0f} minute(s)"

		totalTime = time.time() - dataset["ShiftStartTime"]
		minutes, seconds = divmod(totalTime, 60)
		if minutes >= 60:
			hours, minutes = divmod(minutes, 60)
			totalTime = f"{hours:.0f} hour(s) {minutes:.0f} minute(s)"
		else:
			totalTime = f"{minutes:.0f} minute(s)"

		return shiftTime, AFKTime, totalTime

from discord.ext import commands

async def update_member(bot: commands.Bot, member: discord.User, guild: discord.Guild):
	added_roles = []
	removed_roles = []

	member = guild.get_member(member.id)
	if member is None or guild.name == "Logging Server":
		return added_roles, removed_roles, None

	extras = guild.get_role(1069671401235157073)
	nitroBooster = guild.get_role(1069686292876644402)
	flex = guild.get_role(1069672572410675282)
	colour_roles = ['Electric', 'Lemon', 'Cyan', 'Mango', 'Bubblegum', 'Lime', 'Scarlet', 'Purple', 'Orange']

	dataset = await bot.roblox.find_by_id(member.id)
	RBLXdataset = dataset
	if dataset:
		robloxID = dataset['roblox']
		robloxUser = await client.get_user(dataset['roblox'])
		robloxUsername = robloxUser.name

		if dataset['banned'] == True:
			for guild in bot.guilds:
				await guild.ban(member, reason=f"User linked to a banned ROBLOX account.")
			nickname = member.nick
			return added_roles, removed_roles, nickname

		suspended = discord.utils.get(guild.roles, name="Suspended")
		
		if dataset['suspended'] == True:
			for i in member.roles:
				try:
					await member.remove_roles(i)
				except:
					pass
			if suspended and suspended not in member.roles:
				await member.add_roles(suspended)
				added_roles.append(suspended.id)
			await member.edit(nick=f"[SUSPENDED] {robloxUsername}")
			nickname = f"[SUSPENDED] {robloxUsername}"
			return added_roles, removed_roles, nickname
		elif dataset['suspended'] == False:
			if suspended and suspended in member.roles:
				removed_roles.append(suspended.id)

		if guild.id == 1069662276728143913:
			verified = guild.get_role(1069671804429406218)
			if verified not in member.roles:
				added_roles.append(verified.id)
			if extras not in member.roles:
				added_roles.append(extras.id)
	else:
		if guild.id == 1069662276728143913:
			verified = guild.get_role(1069671804429406218)
			if verified in member.roles:
				removed_roles.append(verified.id)
			if extras in member.roles:
				removed_roles.append(extras.id)

	if guild.id == 1069662276728143913:
		if nitroBooster in member.roles:
			if flex not in member.roles:
				added_roles.append(flex.id)
		else:
			for role in member.roles:
				if role.name in colour_roles and role != flex:
					removed_roles.append(role.id)
			if flex in member.roles:
				removed_roles.append(flex.id)

	async def get_ba_rank(groups_data):
		group_id = 15356653
		userBARank = None

		for group in groups_data:
			if group['group']['id'] == group_id:
				userBARank = group['role']['rank']
				break

		if userBARank is None:
			return "CIV"

		api_url = f'https://groups.roblox.com/v1/groups/{group_id}/roles'
		response = requests.get(api_url)
		ranks_data = response.json()

		for role in ranks_data['roles']:
			if role['rank'] == userBARank:
				role_name = role['name']
				match = re.search(r'\[(.*?)\]', role_name)
				if match:
					return match.group(1)
	
	dataset = await bot.rankbinds.find_by_id(guild.id)
	if dataset:
		has_an_access_pass = any(rankbind['access_pass'] == False for rankbind in dataset["rankbinds"])

		if not has_an_access_pass and (dataset := await bot.rankbinds.find_by_id(guild.id)) and dataset['locked']:
			unauthorisedAccess = discord.Embed(
				title="Unauthorised Access",
				description=f"You have been removed from the server `{guild.name}` as you do not have an access pass. Please rejoin once you have obtained an access pass to this server.",
				color=0xff0000
			)
			try:
				await member.send(embed=unauthorisedAccess)
			except:
				pass
			await member.kick(reason="Unauthorised Access (No Access Pass)")

	highest_priority = 0
	highest_priority_template = None
	if RBLXdataset:
		highest_priority_template = "[{ba-rank}] {roblox-username}"

	rankbinds_met = []

	if RBLXdataset and dataset:
		api_url = f'https://groups.roblox.com/v2/users/{robloxID}/groups/roles'
		response = requests.get(api_url)
		groups_data = response.json()['data']

		for rankbind in dataset['rankbinds']:
			nickname_template = rankbind['nickname_template']
			nickname_priority = rankbind['nickname_priority']
			role_ids = rankbind['role']

			if is_user_in_group_with_rank(groups_data, rankbind['group_id'], rankbind['rank_id']):
				for role_id in role_ids:
					role = guild.get_role(role_id)
					if role:
						rankbinds_met.append(role.id)
						if role and role not in member.roles:
							if role.id not in added_roles:
								added_roles.append(role.id)

				if nickname_priority >= highest_priority:
					highest_priority = nickname_priority
					highest_priority_template = nickname_template
			else:
				for role_id in role_ids:
					role = guild.get_role(role_id)
					if role and role in member.roles:
						if role.id not in removed_roles:
							removed_roles.append(role.id)

	for role in added_roles:
		await member.add_roles(guild.get_role(role))

	rolesRemoved = []

	for role in removed_roles:
		if role in rankbinds_met:
			continue
		if role not in rankbinds_met:
			roleObject = guild.get_role(role)
			await member.remove_roles(roleObject)
			rolesRemoved.append(role)

	nickname = None
	if RBLXdataset:
		nickname = highest_priority_template.replace("{roblox-username}", robloxUsername)
		nickname = nickname.replace('{display-name}', robloxUser.display_name)
		ba_rank = await get_ba_rank(groups_data)
		nickname = nickname.replace('{ba-rank}', ba_rank)

	try:
		await member.edit(nick=nickname)
	except:
		pass

	return added_roles, rolesRemoved, nickname

async def get_admin_level(bot, guild, user_id):
	dataset = await bot.admins.find_by_id(guild.id)
	admin_level = 0

	user_id = int(user_id)

	user = await guild.fetch_member(user_id)

	if dataset:
		admins = sorted(dataset['admins'], key=lambda x: int(x['AdminLevel']))

		for admin in admins:
			role = discord.utils.get(guild.roles, id=admin['MemberOrRole'])
			if role:
				if role in user.roles:
					if int(admin['AdminLevel']) > admin_level:
						admin_level = int(admin['AdminLevel'])
			else:
				if int(admin['MemberOrRole']) == int(user.id):
					if int(admin['AdminLevel']) > int(admin_level):
						admin_level = admin['AdminLevel']

	if user_id in owners:
		admin_level = float('inf')
	
	return admin_level

async def createTicket(bot, ctx, type, message=None):
	type = int(type)
	category = discord.utils.get(ctx.guild.categories, id=1091254812819066891)

	if type == 8:
		ticketType = "dstransfer"
	elif type == 2 or type == 3 or type == 7 or type == 9 or type == 10 or type == 11 or type == 12 or type == 14:
		ticketType = "report"
	elif type == 1 or type == 4 or type == 5 or type == 6 or type == 13:
		if type == 1:
			ticketType = "bug"
		elif type == 4:
			ticketType = "exploit"
		elif type == 5:
			ticketType = "devapp"
		elif type == 6:
			ticketType = "alliance"
		elif type == 13:
			ticketType = "veteran"

	if type != 12 and type != 13 and type != 14:
		ticketCreator = ctx.user

		ticketTypes = []

		for channel in category.channels:
			if isinstance(channel, discord.TextChannel):
				if channel.topic and str(ticketCreator.id) in channel.topic:
					ticketTypes.append(channel.name.split('-')[0])
		if ticketType in ticketTypes:
			openTicket = discord.Embed(title="Report Ticket", description=f"There is already an open ticket at {channel.mention}", color=discord.Color.dark_blue())
			openTicket.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)
			return await ctx.followup.send(embed=openTicket, ephemeral=True)
	elif type == 12 or type == 14:
		if type == 12:
			ticketCreator = ctx.author
			reportedMessage = await ctx.fetch_message(ctx.message.reference.message_id)
		else:
			ticketCreator = ctx.user
			reportedMessage = message
		contentReported = reportedMessage.content
		if reportedMessage.author.nick == None:
			reportedMessageAuthorNickname = reportedMessage.author.name
		else:
			reportedMessageAuthorNickname = reportedMessage.author.nick
		contentSentBy = f"{reportedMessage.author.mention} | {reportedMessageAuthorNickname} | {reportedMessage.author.id}"
		jumpToMessage = reportedMessage.jump_url
	elif type == 13:
		ticketCreator = ctx.author

	ticket_number = 1

	for channel in category.channels:
		if isinstance(channel, discord.TextChannel):
			if channel.name.split('-')[0] == ticketType:
				ticket_number += 1
	
	name = f"{ticketType}-{ticket_number}"

	supportTeam = ctx.guild.get_role(1069672694175506463)

	if type != 12 and type != 13 and type != 14:
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ctx.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					supportTeam: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=f"otherReport:{ctx.user.id}", overwrites = overwrites, category=category)

		ticketCreated = discord.Embed(title="Report Ticket", description=f"Your report ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
		ticketCreated.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
		await ctx.followup.send(embed=ticketCreated, ephemeral=True)
	elif type == 12 or type == 14:
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ticketCreator: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					reportedMessage.author: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					supportTeam: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=f"contentReport:{ticketCreator.id}", overwrites = overwrites, category=category)
		if type == 14:
			ticketCreated = discord.Embed(title="Report Ticket", description=f"Your report ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
			ticketCreated.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
			await ctx.response.send_message(embed=ticketCreated, ephemeral=True)
		elif type == 12:
			ticketCreated = discord.Embed(title="Report Ticket", description=f"Your report ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
			ticketCreated.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)
			await ctx.send(embed=ticketCreated)
	elif type == 13:
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ctx.author: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					supportTeam: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=f"otherReport:{ctx.author.id}", overwrites = overwrites, category=category)
	
	welcomeEmbed = discord.Embed(title=f"**{channel.name.split('-')[0].upper()} TICKET**", color=discord.Color.dark_blue())

	if type == 1:
		welcomeEmbed.description="Hello! This is your Report ticket to report a glitch or bug. Please send us the following information.\n```Username:\nProfile Link:\nGlitch/Bug:\nDescribe it:\nImage/Videos:\nSteps to Replicate:```"
	elif type == 2:
		welcomeEmbed.description="Hello! This is your Report ticket to report a High rank. Please send us the following information about that officer.\n```Username:\nRank:\nExplain their behaviour:\nImage/Videos:```"
	elif type == 3:
		welcomeEmbed.description="Hello! This is your Report ticket to report an exploiter. Please send us the following information.\n```Exploiter:\nExplain:\nImage/Videos:```"
	elif type == 4:
		welcomeEmbed.description="Hello! This is your report ticket to report a script that works to exploit our game. Please send us the following information about the script.\n```Exploit name:\nWhat it does:\nHow to do it:\nHow did you get this:\nImage/Videos:```"
	elif type == 5:
		welcomeEmbed.description="Hello! This is your ticket to apply as a developer in Alfie's Dev Team. Please send us the following information.\n```Username:\nProfile Link:\nType of Developer:\nDevForum Portfolio:\nGroups Work History:\nImage/Videos:```"
	elif type == 6:
		welcomeEmbed.description="Hello! This is your ticket to request an alliance with Roblox |ABA| British Army group. Please send us the following information.\n```Roblox Username:\nYour rank there:\nGroup Name:\nOwned By:\nGroup link:\nMain Game link:\nReason for alliance:```"
	elif type == 7:
		welcomeEmbed.description="Hello! This is your Report ticket to report corruption. Please send us the following information about the corrupt individual\n```Username:\nRank:\nRegiment:\nExplain:\nImage/Videos:```"
	elif type == 8:
		welcomeEmbed.description="Hello! This is your ticket to request a transfer from your old discord to a new discord. Please send us the following information about you.\n```Username:\nRank:\nDivision:\nDivision Rank:\nOld Discord:\nExplain:\nImage/Videos:```"
	elif type == 9:
		welcomeEmbed.description="Hello! This is your Report ticket to report an abuser. Please send us the following information about the abuser.\n```Username:\nRegiment:\nRank:\nExplain:\nImage/Videos:```"
	elif type == 10:
		welcomeEmbed.description="Hello! This is your Report ticket to report a rule breaker in DMs or BA chat. Please send us the following information about the individual.\n```Username:\nRank:\nExplain their actions:\nImage/Videos:```"
	elif type == 11:
		welcomeEmbed.description="**Unfair Mute Report Ticket**\n\nAll mods, please do not intervene into this ticket and escalate it to an administrator immediately, failure to do so would result in a removal.\n\nModerator Reported: {ctx.author.nick}\nMute Duration: {duration}\nMute Reason: {reason}"
	elif type == 12 or type == 14:
		welcomeEmbed.description=f"Content Reported : {contentReported}\n\nContent Sent By : {contentSentBy}\n\nJump To Message : {jumpToMessage}"
	elif type == 13:
		welcomeEmbed.description="Hello! This is your ticket to gain your rank in the Veteran Association group. Please send us the following information about you.\n```Username:\nRank:\nRegiment:\nYear Joined:\nImage/Videos:```"
	
	if type != 12 and type != 13 and type != 14:
		welcomeEmbed.set_author(name=f"{ctx.user.name}", icon_url=ctx.user.avatar)
		message = await channel.send(f"{ctx.user.mention}, {supportTeam.mention}", embed=welcomeEmbed)
	elif type == 12 or type == 14:
		welcomeEmbed.set_author(name=f"{ticketCreator.name}", icon_url=ticketCreator.avatar)
		message = await channel.send(f"{ticketCreator.mention}, {reportedMessage.author.mention}, {supportTeam.mention}", embed=welcomeEmbed)
	elif type == 13:
		welcomeEmbed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
		message = await channel.send(f"{ctx.author.mention}, {supportTeam.mention}", embed=welcomeEmbed)

	def check(m):
		if m.author.bot:
			return False
		return supportTeam in m.author.roles and m.channel == channel
	
	response = await bot.wait_for("message", check=check)
	
	supportArrived = discord.Embed(
		title="**Support has arrived!**",
		description=f"{response.author.mention} will now be assisting with your report.",
		color=discord.Color.dark_blue(),
	)
	supportArrived.set_author(name=f"{response.author.name}", icon_url=response.author.avatar)
	await channel.send(ticketCreator.mention, embed=supportArrived)

	claimedMod = response.author
	await channel.edit(topic=f"{channel.topic}-{claimedMod.id}")