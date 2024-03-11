import typing

import discord

import motor.motor_asyncio
from utils.mongo import Document

import datetime
import requests
from roblox import Client
client = Client()

import math

class Pagination(discord.ui.View):
	def __init__(self, user_id: int, embeds: list, extras: list = None):
		super().__init__(timeout=None)
		if extras is not None:
			for item in extras:
				self.add_item(item)

		self.user_id = user_id
		self.embeds = embeds
		self.current_index = 0
		if len(embeds) == 1:
			for button in self.children:
				if isinstance(button, discord.ui.Button):
					if button.label in ["Previous Page", "Next Page"]:
						self.remove_item(button)



	async def paginate(self, message, change_pages: int):
		self.current_index += change_pages
		try:
			embed = self.embeds[self.current_index]
		except:
			return ValueError(
				"Index could not be found in embed list. Should be caught."
			)
		
		if self.current_index == 0:
			for button in self.children:
				if isinstance(button, discord.ui.Button):
					if button.label == "Previous Page":
						button.disabled = True

		if self.current_index > 0:
			for button in self.children:
				if isinstance(button, discord.ui.Button):
					if button.label == "Previous Page":
						button.disabled = False

		if (self.current_index + 1) == len(self.embeds):
			for button in self.children:
				if isinstance(button, discord.ui.Button):
					if button.label == "Next Page":
						button.disabled = True
				
		if (self.current_index + 1) < len(self.embeds):
			for button in self.children:
				if isinstance(button, discord.ui.Button):
					if button.label == "Next Page":
						button.disabled = False

		from copy import copy
		new_embed = copy(embed)
		new_embed.set_footer(text=f"Viewing page {self.current_index + 1} / {len(self.embeds)}")

		await message.edit(embed=new_embed, view=self)

	@discord.ui.button(style=discord.ButtonStyle.primary, label="Previous Page", disabled=True)
	async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		if interaction.user.id != self.user_id:
			invalidAction=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This button does not belong to you',
				color = discord.Color.dark_gold(),
			)
			invalidAction.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.followup.send(embed=invalidAction, ephemeral=True)
		await self.paginate(interaction.message, -1)

	@discord.ui.button(style=discord.ButtonStyle.primary, label="Next Page", disabled=False)
	async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		if interaction.user.id != self.user_id:
			invalidAction=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This button does not belong to you',
				color = discord.Color.dark_gold(),
			)
			invalidAction.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.followup.send(embed=invalidAction, ephemeral=True)
		await self.paginate(interaction.message, 1)

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

class EvidenceInput(discord.ui.Modal, title="Moderate User"):
	evidence = discord.ui.TextInput(label='Input evidence of rule(s) violation', placeholder="Input the gyazo links showing the user violating the rules, and seperate them into lines if multiple", max_length=None,
								style=discord.TextStyle.long, required=True)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		self.stop()

"""
class RuleDropdown(discord.ui.Select):
	def __init__(self, member, actionType, bot, options: list):
		self.member = member
		self.actionType = actionType
		self.bot = bot
		self.modal: typing.Union[None, EvidenceInput] = None
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above
		super().__init__(placeholder='Select Rule(s) Violated', max_values=len(optionList), options=optionList)

	async def callback(self, interaction: discord.Interaction):
		if len(self.values) == 1:
			self.view.value = self.values[0]
		else:
			self.view.value = self.values

		self.modal = EvidenceInput()
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		evidence = self.modal.evidence.value
		evidence = evidence.split('\n')

		reason = []
		actionReason = []
		for rule in sorted(self.view.value, key=int):
			rule_label = f"Rule {int(rule)}"
			actionReason.append(rule_label)
			rule_detail = optionsDict.get(int(rule))["description"]
			if rule_detail:
				reason.append(f"{rule_label}. {rule_detail}")

		moderationReason = "\n".join(reason)
		actionReason = ", ".join(actionReason)
		actionReason = sorted(self.view.value, key=int)

		moderationDuration = ""

		timeout_duration = 0

		for eachRule in self.view.value:
			timeout_duration += optionsDict.get(int(rule))["duration"]

		if await self.bot.actions.find_by_id(self.member.id):
			timeout_duration = timeout_duration * 2

		hours = timeout_duration
		moderationDuration = f"{hours}h"
		
		if self.actionType == "Kick":
			moderationDuration = "N/A"

		evidenceList = []
		for each in evidence:
			evidenceList.append(each)

		evidenceLog = "\n".join(evidenceList)

		moderationLog = discord.Embed(title="Moderation Logs", description=f"Moderator: {interaction.user.mention}\nModerated User: {self.member.mention} | {self.member.display_name} | {self.member.name}#{self.member.discriminator}\nModeration Action: {self.actionType}\nModeration Duration: {moderationDuration}", color=discord.Color.dark_blue())
		moderationLog.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
		moderationLog.add_field(name="Rule(s) Violated", value=f"```{moderationReason}```", inline=False)
		moderationLog.add_field(name="Evidence", value=f"```{evidenceLog}```", inline=False)
		moderationLog.add_field(name="Additional Information", value="N/A", inline=False)
		modLogs = interaction.guild.get_channel(1069671496244539443)
		await modLogs.send(embed=moderationLog)

		moderationConfirmation = discord.Embed(title="Moderate User", description=f"Successfully moderated user {self.member.mention}\n\nModeration Action taken: {self.actionType}\n\nModeration Duration: {moderationDuration}\n\nAdditional Information: N/A", color=discord.Color.dark_blue())
		moderationConfirmation.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
		await interaction.edit_original_response(embed=moderationConfirmation, view=None)

		moderationNotice = discord.Embed(title="Moderation Notice", description=f"You have been moderated in {interaction.guild.name} server.\n\nModeration Action Taken: {self.actionType}\n\nModeration Duration: {moderationDuration}\n\nReason:\n```{moderationReason}```", color=discord.Color.dark_gold())
		moderationNotice.set_author(name=self.member.name, icon_url=self.member.avatar)
		try:
			await self.member.send(embed=moderationNotice)
		except:
			pass

		actionID = 0
		for item in await self.bot.actions.get_all():
			for action in item["actions"]:
				actionID += 1
		actionID += 1

		default_action_item = {
			'_id': self.member.id,
			'actions': [{
				'id': actionID,
				"Type": self.actionType,
				"Date": interaction.message.created_at.strftime('%Y-%m-%d'),
				"Moderator": interaction.user.id,
				"Reason": actionReason,
				"Duration": moderationDuration,
				"Evidence": evidence,
				"Server": interaction.guild.id
			}]
		}

		singular_action_item = {
				'id': actionID,
					"Type": self.actionType,
					"Date": interaction.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": interaction.user.id,
					"Reason": actionReason,
					"Duration": moderationDuration,
					"Evidence": evidence,
					"Server": interaction.guild.id
			}
		
		async def insertModerationAction():
			default_moderation_item = {
				'_id': self.member.id,
				'moderations': [{
					"Id": actionID,
					"Type": self.actionType,
					"Duration": timeout_duration,
					"Time": datetime.datetime.now(),
					"Server": interaction.guild.id
				}]
			}

			singular_moderation_item = {
					"Id": actionID,
						"Type": self.actionType,
						"Duration": timeout_duration,
						"Time": datetime.datetime.now(),
						"Server": interaction.guild.id
				}
			
			if not await self.bot.moderations.find_by_id(self.member.id):
				await self.bot.moderations.insert(default_moderation_item)
			else:
				dataset = await self.bot.moderations.find_by_id(self.member.id)
				dataset['moderations'].append(singular_moderation_item)
				await self.bot.moderations.update_by_id(dataset)

		if self.actionType == "Watchlist":
			await insertModerationAction()
			watchlistRole = interaction.guild.get_role(1114610855116558336)
			await self.member.add_roles(watchlistRole)
		elif self.actionType == "Suspension":
			await insertModerationAction()
			dataset = await self.bot.roblox.find_by_id(self.member.id)

			if dataset:
				for details in dataset['account']:
					suspended = str(details['suspended'])

				suspended = suspended.lower()

				default_roblox_item = {
					'_id': dataset['discord'],
					'roblox': dataset['roblox'],
					'banned': dataset['banned'],
					'suspended': True,
				}

				await self.bot.roblox.update(default_roblox_item)
		elif self.actionType == "Kick":
			await self.member.kick(reason=f"{actionReason}. - {interaction.user.nick}")
		elif self.actionType == "Timeout":
			timeoutDuration = datetime.timedelta(days=0, hours=hours, seconds=0, microseconds=0)
			await self.member.timeout(timeoutDuration, reason=f"{actionReason}. - {interaction.user.nick}")
		elif self.actionType == "Ban":
			await insertModerationAction()
			for guild in self.bot.guilds:
				await guild.ban(self.member, reason=f"{actionReason}. - {interaction.user.nick} | Banned in {interaction.guild.name}")

		if not await self.bot.actions.find_by_id(self.member.id):
			await self.bot.actions.insert(default_action_item)
		else:
			dataset = await self.bot.actions.find_by_id(self.member.id)
			dataset['actions'].append(singular_action_item)
			await self.bot.actions.update_by_id(dataset)

class RuleSelectionMenu(discord.ui.View):
	def __init__(self, member, actionType, bot, options: list):
		super().__init__(timeout=None)
		self.value = None
		self.member = member
		self.actionType = actionType
		self.bot = bot

		self.add_item(RuleDropdown(self.member, self.actionType, self.bot, options))
"""

class PromotionRequest(discord.ui.View):
	def __init__(self, bot, user, originalRank, nextRank, promoter):
		super().__init__(timeout=None)
		self.value = None
		self.bot = bot
		self.user = user
		self.originalRank = originalRank
		self.nextRank = nextRank
		self.promoter = promoter

	# When the confirm button is pressed, set the inner value to `True` and
	# stop the View from listening to more input.
	# We also send the user an ephemeral message that we're confirming their choice.
	@discord.ui.button(label='Accept Promotion', style=discord.ButtonStyle.green)
	async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		await interaction.message.delete()
		rankingLogs = self.bot.get_channel(1069671316724125838)
		successfulPromotion = discord.Embed(color=0x4dfe0c)
		successfulPromotion.description = f"SUCCESSFULLY PROMOTED {self.user.name} FROM **{self.originalRank}** TO **{self.nextRank}**\n**PROMOTER:** {self.promoter.name}\n**APPROVED BY:** {interaction.user.mention}"
		await rankingLogs.send(embed=successfulPromotion)
		api_url = f'https://aba-ranking-services-fad267650515.herokuapp.com/promote?key=psxap8ikeyhasawnwfs2ua3ynoiuqwanyeuo1ang7oisuhqw&userid={self.user.id}'
		response = requests.get(api_url)

	# This one is similar to the confirmation button except sets the inner value to `False`
	@discord.ui.button(label='Deny Promotion', style=discord.ButtonStyle.red)
	async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		await interaction.message.delete()

class CustomRankbinds(discord.ui.Select):
	def __init__(self, user_id, options: list, bot):
		self.user_id = user_id
		self.bot = bot
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above
		super().__init__(placeholder='Select Group To View Rankbinds', min_values=1, max_values=1, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)

		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
			self.placeholder = self.view.value.title()
		else:
			self.view.value = self.values

		dataset = await self.bot.rankbinds.find_by_id(interaction.guild.id)
		rankbinds = dataset['rankbinds']

		viewingRankbinds = discord.Embed(
			title=f"Viewing Rankbinds For {interaction.guild.name}",
			color=discord.Color.dark_blue(),
		)
		viewingRankbinds.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		totalRankbindsForGroup = int(0)
		embeds = []
		embeds.append(viewingRankbinds)
		for rankbind in rankbinds:
			if rankbind['group_id'] == int(self.view.value):
				totalRankbindsForGroup += 1
				rank_ids = rankbind['rank_id']
				nickname_template = rankbind['nickname_template']
				nickname_priority = rankbind['nickname_priority']
				access_pass = str(rankbind['access_pass']).lower()

				mentioned_roles = [interaction.guild.get_role(role_id).mention for role_id in rankbind['role'] if interaction.guild.get_role(role_id)]
				role_mention = " ".join(mentioned_roles) if mentioned_roles else "None"

				if len(embeds[-1].fields) == 4:
						new_embed = discord.Embed(
							title=f"Viewing Rankbinds For {interaction.guild.name}",
							color=discord.Color.dark_blue(),
						)
						new_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
						embeds.append(new_embed)
						embeds[-1].add_field(
							name=f"Rank: {rank_ids}",
							value=f"Nickname Template : `{nickname_template}`\nNickname Priority : {nickname_priority}\nRoles Binded : {role_mention}\nAccess Pass : {access_pass}",
							inline=False
						)
				else:
					embeds[-1].add_field(
						name=f"Rank: {rank_ids}",
						value=f"Nickname Template : `{nickname_template}`\nNickname Priority : {nickname_priority}\nRoles Binded : {role_mention}\nAccess Pass : {access_pass}",
						inline=False
					)
		for embed in embeds:
			embed.description=f"Viewing group {self.view.value} | Total {totalRankbindsForGroup} Rankbinds"
		embeds[0].set_footer(text=f"Viewing page 1 / {len(embeds)}")
		new_view = Pagination(
			interaction.user.id,
			embeds,
			[
				self
			]
		)
		await interaction.message.edit(embed=embeds[0], view=new_view)

class CustomRankbindsMenu(discord.ui.View):
	def __init__(self, user_id, options: list, bot):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

		self.add_item(CustomRankbinds(self.user_id, options, bot))

class CustomCommands(discord.ui.Select):
	def __init__(self, user_id, options: list, commands: list):
		self.user_id = user_id
		self.commands = commands
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above
		super().__init__(placeholder='Select Command Categories', min_values=1, max_values=1, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)

		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
			self.placeholder = self.view.value.title()
		else:
			self.view.value = self.values

		viewCommandCategory = discord.Embed(
			title=f"Command Category : {self.view.value}",
			description=f"Viewing commands for {self.view.value}",
			color=discord.Color.dark_blue(),
		)
		viewCommandCategory.set_author(name=f"{interaction.user.name}", icon_url=interaction.user.avatar)
		embeds = []
		embeds.append(viewCommandCategory)
		for command in self.commands:
			if command.category == self.view.value:
				if command.description == "":
					commandDescription = "No Description Specified."
				else:
					commandDescription = command.description

				if command.usage == None:
					commandUsage = "No Usage Provided."
				else:
					commandUsage = command.usage

				try:
					commandAdminLevel = command.extras['levelPermissionNeeded']
					if math.isinf(commandAdminLevel):
						commandAdminLevel = "Infinity"
				except:
					commandAdminLevel = 0

				try:
					if command.with_app_command == True:
						commandPrefix = "/"
					else:
						commandPrefix = "!"
				except:
					commandPrefix = "!"
				
				if len(embeds[-1].fields) == 4:
						new_embed = discord.Embed(
							title=f"Command Category : {self.view.value}",
							description=f"Viewing commands for {self.view.value}",
							color=discord.Color.dark_blue(),
						)
						new_embed.set_author(name=f"{interaction.user.name}", icon_url=interaction.user.avatar)
						embeds.append(new_embed)
						embeds[-1].add_field(
							name=f"{commandPrefix}{command.full_name}",
							value=f"Command Description: {commandDescription}\nCommand Usage: {commandUsage}\nAdmin Level: {commandAdminLevel}",
							inline=False
						)
				else:
					embeds[-1].add_field(
						name=f"{commandPrefix}{command.full_name}",
						value=f"Command Description: {commandDescription}\nCommand Usage: {commandUsage}\nAdmin Level: {commandAdminLevel}",
						inline=False
					)

		embeds[0].set_footer(text=f"Viewing page 1 / {len(embeds)}")
		new_view = Pagination(
			interaction.user.id,
			embeds,
			[
				self
			]
		)
		await interaction.message.edit(embed=embeds[0], view=new_view)

class CustomCommandsMenu(discord.ui.View):
	def __init__(self, user_id, options: list, commands: list):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

		self.add_item(CustomCommands(self.user_id, options, commands))

class CustomActions(discord.ui.Select):
	def __init__(self, user_id, options: list, member: discord.Member, bot):
		self.user_id = user_id
		self.member = member
		self.bot = bot
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above
		super().__init__(placeholder='Select Action Type', min_values=1, max_values=1, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)

		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
			self.placeholder = self.view.value.title()
		else:
			self.view.value = self.values

		dataset = await self.bot.actions.find_by_id(self.member.id)

		try:
			if self.member.nick:
				memberNickname = self.member.nick
			else:
				memberNickname = self.member.name
		except:
			memberNickname = self.member.name

		if self.view.value == "all":
			item = dataset['actions']
		else:
			item = [action for action in dataset['actions'] if action["Type"].lower() == self.view.value]
		viewActionHistory = discord.Embed(
			title=f"Viewing Action History For {memberNickname}",
			description=f"Viewing action type : **{self.view.value.title()}**\n**Total {self.view.value.title()} Actions**\n{len(item)}\n**\n{self.view.value.title()} History**",
			color=discord.Color.dark_blue(),
		)
		viewActionHistory.set_author(name=f"{interaction.user.name}", icon_url=interaction.user.avatar)
		embeds = []
		embeds.append(viewActionHistory)
		for action in item:
			try:
				guildName = self.bot.get_guild(action['Server']).name
			except:
				guildName = "Unknown Server"
			action_reason = action['Reason']
			if isinstance(action_reason, list):
				actionReason = []
				for rule in sorted(action_reason, key=int):
					rule_label = f"Rule {int(rule)}"
					actionReason.append(rule_label)
				action_reason = ", ".join(actionReason)
			if len(embeds[-1].fields) == 4:
						new_embed = discord.Embed(
							title=f"Viewing Action History For {memberNickname}",
							description=f"Viewing action type : **{self.view.value.title()}**\n**Total {self.view.value.title()} Actions**\n{len(item)}\n**\n{self.view.value.title()} History**",
							color=discord.Color.dark_blue(),
						)
						new_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
						embeds.append(new_embed)
						embeds[-1].add_field(
							name=f"\n",
							value=f"**ACTION ID:** #{action['id']}\n**ACTION TYPE:** {action['Type']}\n**ACTION DATE:** {action['Date']}\n**ACTION BY:** <@{action['Moderator']}>\n**ACTION INFO:** {action_reason}\n**SERVER:** {guildName}",
							inline=False
						)
			else:
				embeds[-1].add_field(
					name=f"\n",
					value=f"**ACTION ID:** #{action['id']}\n**ACTION TYPE:** {action['Type']}\n**ACTION DATE:** {action['Date']}\n**ACTION BY:** <@{action['Moderator']}>\n**ACTION INFO:** {action_reason}\n**SERVER:** {guildName}",
					inline=False
				)
		embeds[0].set_footer(text=f"Viewing page 1 / {len(embeds)}")

		new_view = Pagination(
				interaction.user.id,
				embeds,
				[
					self
				]
			)
		await interaction.message.edit(embed=embeds[0], view=new_view)

class CustomActionsMenu(discord.ui.View):
	def __init__(self, user_id, options: list, member: discord.Member, bot):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

		self.add_item(CustomActions(self.user_id, options, member, bot))

class CustomEscalate(discord.ui.Select):
	def __init__(self, bot, user_id, options: list, limit=1):
		self.bot = bot
		self.user_id = user_id
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		super().__init__(placeholder='Select Role', min_values=1, max_values=limit, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
		else:
			self.view.value = self.values

		ticketCreatorID, ticketClaimerID = interaction.channel.topic.split("-")
		ticketCreatorID = int(ticketCreatorID.split(":")[1])

		if "/" in ticketClaimerID:
			ticketClaimerID = int(ticketClaimerID.split("/")[0])
		else:
			ticketClaimerID = int(ticketClaimerID)

		ticketCreator = await self.bot.fetch_user(ticketCreatorID)

		roles = {
			"moderator": 1069674122642206771,
			"administrator": 1069667659563683850,
			"tester": [1120757812117635103, 1069676208985485462],
			"developer": 1069676208985485462,
			"sib": 1069671923220480010,
			"cos": 1069664070921363596,
		}

		role_ids = roles.get(self.view.value)
		overwrites = {
			interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
			ticketCreator: discord.PermissionOverwrite(
				view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True
			),
		}

		if isinstance(role_ids, int):
			role = interaction.guild.get_role(role_ids)
			overwrites[role] = discord.PermissionOverwrite(
				view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True,
				use_application_commands=True,
			)
		elif isinstance(role_ids, list):
			role = interaction.guild.get_role(role_ids[0])
			for eachRole in role_ids:
				overwrites[interaction.guild.get_role(eachRole)] = discord.PermissionOverwrite(
					view_channel=True, read_message_history=True, send_messages=True, attach_files=True, embed_links=True,
					use_application_commands=True,
				)

		newTopic = interaction.channel.topic.split("/")[0] if "/" in interaction.channel.topic else interaction.channel.topic
		newTopic = f"{newTopic}/{role.id}"
		await interaction.channel.edit(overwrites=overwrites, topic=newTopic)

		escalatedTicket = discord.Embed(
			title="Escalated Ticket",
			description="This ticket has been escalated to you by the support team. Please handle this ticket.\n\n`/tickets close` to close the ticket after resolving it.\n`/tickets escalate` to re-escalate this ticket to another team.",
			color=discord.Color.dark_blue(),
		)
		escalatedTicket.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)

		await interaction.channel.send(f"{ticketCreator.mention}, {role.mention}", embed=escalatedTicket)

class CustomEscalateMenu(discord.ui.View):
	def __init__(self, bot, user_id, options: list):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

		self.add_item(CustomEscalate(bot, self.user_id, options))

class CloseTicket(discord.ui.View):
	def __init__(self, user_id):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

	@discord.ui.button(label='Yes (Close Ticket)', style=discord.ButtonStyle.green)
	async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)
		await interaction.response.defer()
		for item in self.children:
			item.disabled = True
		self.value = True
		await interaction.edit_original_response(view=self)
		self.stop()

	@discord.ui.button(label='No (Keep Ticket Open)', style=discord.ButtonStyle.red)
	async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)
		await interaction.response.defer()
		for item in self.children:
			item.disabled = True
		self.value = False
		await interaction.edit_original_response(view=self)
		self.stop()

class ReportAbuse(discord.ui.View):
	def __init__(self, user_id):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

	# When the confirm button is pressed, set the inner value to `True` and
	# stop the View from listening to more input.
	# We also send the user an ephemeral message that we're confirming their choice.
	@discord.ui.button(label='Report Abuse', style=discord.ButtonStyle.red, emoji="⚠️")
	async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)
		await interaction.response.defer()
		for item in self.children:
			item.disabled = True
		self.value = True
		await interaction.edit_original_response(view=self)
		self.stop()

class CustomErrors(discord.ui.Select):
	def __init__(self, user_id, options: list, bot):
		self.user_id = user_id
		self.bot = bot
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above
		super().__init__(placeholder='Select Error Server', min_values=1, max_values=1, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)

		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
			self.placeholder = self.view.value.title()
		else:
			self.view.value = self.values

		dataset = await self.bot.errors.get_all()
		if self.view.value == "all":
			item = dataset
			selectedErrorGuild = "All"
		else:
			item = []
			try:
				selectedErrorGuild = self.bot.get_guild(int(self.view.value)).name
			except:
				selectedErrorGuild = "Unknown Server"
			for error in dataset:
				if error['guild'] == int(self.view.value):
					item.append(error)

		listErrors = discord.Embed(
			title=f"Listing Errors For {selectedErrorGuild}",
			description=f"**Total Errors**\n**{len(item)}**",
			color=discord.Color.dark_blue(),
		)
		listErrors.set_author(name=f"{interaction.user.name}", icon_url=interaction.user.avatar)
		embeds = []
		embeds.append(listErrors)
		for error in item:
			try:
				guildName = self.bot.get_guild(error['guild']).name
			except:
				guildName = "Unknown Server"
			if len(embeds[-1].fields) == 4:
				new_embed = discord.Embed(
					title=f"Listing Errors For {selectedErrorGuild}",
					description=f"**Total Errors**\n**{len(item)}**",
					color=discord.Color.dark_blue(),
				)
				new_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
				embeds.append(new_embed)
				embeds[-1].add_field(
					name=f"\n",
					value=f"**ERROR ID:** {error['_id']}\n**ERROR DATE:** {error['time']}\n**ERROR BY:** <@{error['user']}>\n**ERROR INFO:** {error['error']}\n**SERVER:** {guildName}",
					inline=False
				)
			else:
				embeds[-1].add_field(
					name=f"\n",
					value=f"**ERROR ID:** {error['_id']}\n**ERROR DATE:** {error['time']}\n**ERROR BY:** <@{error['user']}>\n**ERROR INFO:** {error['error']}\n**SERVER:** {guildName}",
					inline=False
				)
		embeds[0].set_footer(text=f"Viewing page 1 / {len(embeds)}")

		new_view = Pagination(
				interaction.user.id,
				embeds,
				[
					self
				]
			)
		await interaction.message.edit(embed=embeds[0], view=new_view)

class CustomErrorsMenu(discord.ui.View):
	def __init__(self, user_id, options: list, bot):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

		self.add_item(CustomErrors(self.user_id, options, bot))

class UnbanAll(discord.ui.View):
	def __init__(self, user_id, bot):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id
		self.bot = bot

	# When the confirm button is pressed, set the inner value to `True` and
	# stop the View from listening to more input.
	# We also send the user an ephemeral message that we're confirming their choice.
	@discord.ui.button(label='Yes (Unban All)', style=discord.ButtonStyle.green)
	async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)
		await interaction.response.defer()
		
		TotalUnbanned = 0
		
		totalBans = 0
		async for ban_entry in interaction.guild.bans():
			totalBans += 1

		unbanStarted = discord.Embed(title="Unban Started", description=f"Please hold on while we unban {totalBans} members", color=discord.Color.dark_blue())
		unbanStarted.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		await interaction.message.edit(embed=unbanStarted, view=None)
		
		async for ban_entry in interaction.guild.bans():
			user = ban_entry.user
			await interaction.guild.unban(user)
			dataset = await self.bot.roblox.find_by_id(user.id)

			if dataset:
				default_action_item = {
					'_id': user.id,
					'roblox': dataset['roblox'],
					'banned': False,
					'suspended': dataset['suspended']
				}

				await self.bot.roblox.update(default_action_item)

			TotalUnbanned += 1

	# This one is similar to the confirmation button except sets the inner value to `False`
	@discord.ui.button(label='No (Cancel)', style=discord.ButtonStyle.red)
	async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
		embed=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This select menu does not belong to you',
				color = discord.Color.dark_gold(),
		)
		embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		if interaction.user.id != self.user_id:
			await interaction.response.defer(ephemeral=True, thinking=True)
			return await interaction.followup.send(embed=embed)
		await interaction.response.defer()
		await interaction.message.delete()

class EvidenceInput(discord.ui.Modal, title="Moderate User"):
	evidence = discord.ui.TextInput(label='Input evidence of rule(s) violation', placeholder="Input the gyazo links showing the user violating the rules, and seperate them into lines if multiple", max_length=None,
								style=discord.TextStyle.long, required=True)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		self.stop()

class RuleDropdown(discord.ui.Select):
	def __init__(self, member, options: list, bot, selectedAction: str=None):
		self.selectedAction = selectedAction
		self.member = member
		self.modal: typing.Union[None, EvidenceInput] = None
		self.bot = bot
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		super().__init__(placeholder='Select Rule(s) Violated', max_values=len(optionList), options=optionList)

	async def callback(self, interaction: discord.Interaction):
		if len(self.values) == 1:
			self.view.value = self.values[0]
		else:
			self.view.value = self.values

		self.modal = EvidenceInput()
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		evidence = self.modal.evidence.value
		evidence = evidence.split('\n')

		reason = []
		actionReason = []
		for rule in sorted(self.view.value, key=int):
			rule_label = f"Rule {int(rule)}"
			actionReason.append(rule_label)
			rule_detail = optionsDict.get(int(rule))["description"]
			if rule_detail:
				reason.append(f"{rule_label}. {rule_detail}")

		actionReason = ", ".join(actionReason)
		actionReason = sorted(self.view.value, key=int)

		moderationDuration = ""

		timeout_duration = 0

		previousRulesBroken = []
		actionCounts = 0

		pastRulesDataset = await self.bot.actions.find_by_id(self.member.id)
		if pastRulesDataset:
			for action in pastRulesDataset["actions"]:
				actionCounts += 1
				if isinstance(action["Reason"], list):
					for rule in sorted(action["Reason"], key=int):
						previousRulesBroken.append(int(rule))

		for eachRule in self.view.value:
			if int(eachRule) in previousRulesBroken:
				timeout_duration += (optionsDict.get(int(eachRule))["duration"] * previousRulesBroken.count(int(eachRule)))
			else:
				timeout_duration += optionsDict.get(int(eachRule))["duration"]

		hours = timeout_duration
		moderationDuration = f"{hours}h"
		additionalInformation = "N/A"

		if self.selectedAction is not None:
			actionType = self.selectedAction
		else:
			if actionCounts <= 5:
				actionType = "Timeout"
			elif actionCounts >= 5:
				actionType = "Suspension"
				additionalInformation = "- Added to Watchlist"

		evidenceList = []
		for each in evidence:
			evidenceList.append(each)

		moderationReasonLog = "\n".join(reason)
		evidenceLog = "\n".join(evidenceList)

		moderationLog = discord.Embed(title="Moderation Logs", description=f"Moderator: {interaction.user.mention}\nModerated User: {self.member.mention} | {self.member.display_name} | {self.member.name}#{self.member.discriminator}\nModeration Action: {actionType}\nModeration Duration: {moderationDuration}", color=discord.Color.dark_blue())
		moderationLog.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
		moderationLog.add_field(name="Rule(s) Violated", value=f"```{moderationReasonLog}```", inline=False)
		moderationLog.add_field(name="Evidence", value=f"```{evidenceLog}```", inline=False)
		moderationLog.add_field(name="Additional Information", value=additionalInformation, inline=False)
		modLogs = interaction.guild.get_channel(1069671496244539443)
		await modLogs.send(embed=moderationLog)

		moderationConfirmation = discord.Embed(title="Moderate User", description=f"Successfully moderated user {self.member.mention}\n\nModeration Action taken: {actionType}\n\nModeration Duration: {moderationDuration}\n\nAdditional Information: {additionalInformation}", color=discord.Color.dark_blue())
		moderationConfirmation.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
		await interaction.edit_original_response(embed=moderationConfirmation, view=None)

		moderationNotice = discord.Embed(title="Moderation Notice", description=f"You have been moderated in {interaction.guild.name} server.\n\nModeration Action Taken: {actionType}\n\nModeration Duration: {moderationDuration}\n\nReason:\n```{moderationReasonLog}```", color=discord.Color.dark_gold())
		moderationNotice.set_author(name=self.member.name, icon_url=self.member.display_avatar.url)
		try:
			await self.member.send(embed=moderationNotice)
		except:
			pass

		actionID = 0
		for item in await self.bot.actions.get_all():
			for action in item["actions"]:
				actionID += 1
		actionID += 1

		default_action_item = {
			'_id': self.member.id,
			'actions': [{
				'id': actionID,
				"Type": actionType,
				"Date": interaction.message.created_at.strftime('%Y-%m-%d'),
				"Moderator": interaction.user.id,
				"Reason": actionReason,
				"Duration": moderationDuration,
				"Evidence": evidence,
				"Server": interaction.guild.id
			}]
		}

		singular_action_item = {
				'id': actionID,
					"Type": actionType,
					"Date": interaction.message.created_at.strftime('%Y-%m-%d'),
					"Moderator": interaction.user.id,
					"Reason": actionReason,
					"Duration": moderationDuration,
					"Evidence": evidence,
					"Server": interaction.guild.id
			}
		
		async def insertModerationAction(moderationActionType):
			default_moderation_item = {
				'_id': self.member.id,
				'moderations': [{
					"Id": actionID,
					"Type": moderationActionType,
					"Duration": timeout_duration,
					"Time": datetime.datetime.now(),
					"Server": interaction.guild.id
				}]
			}

			singular_moderation_item = {
					"Id": actionID,
						"Type": moderationActionType,
						"Duration": timeout_duration,
						"Time": datetime.datetime.now(),
						"Server": interaction.guild.id
				}
			
			if not await self.bot.moderations.find_by_id(self.member.id):
				await self.bot.moderations.insert(default_moderation_item)
			else:
				dataset = await self.bot.moderations.find_by_id(self.member.id)
				dataset['moderations'].append(singular_moderation_item)
				await self.bot.moderations.update_by_id(dataset)

		if actionType == "Watchlist":
			watchlistRole = interaction.guild.get_role(1114610855116558336)
			await self.member.add_roles(watchlistRole)
		elif actionType == "Timeout":
			timeoutDuration = datetime.timedelta(days=0, hours=hours, seconds=0, microseconds=0)
			await self.member.timeout(timeoutDuration, reason=f"{actionReason}. - {interaction.user.nick}")
		elif self.actionType == "Kick":
			await self.member.kick(reason=f"{actionReason}. - {interaction.user.nick}")
		elif actionType == "Suspension":
			await insertModerationAction("Watchlist")
			watchlistRole = interaction.guild.get_role(1114610855116558336)
			await self.member.add_roles(watchlistRole)

			await insertModerationAction("Suspension")
			dataset = await self.bot.roblox.find_by_id(self.member.id)

			if dataset:
				default_action_item = {
					'_id': self.member.id,
					'roblox': dataset['roblox'],
					'banned': dataset['banned'],
					'suspended': True
				}

				await self.bot.roblox.update(default_action_item)
		elif self.actionType == "Ban":
			await insertModerationAction("Ban")
			for guild in self.bot.guilds:
				await guild.ban(self.member, reason=f"{actionReason}. - {interaction.user.nick} | Banned in {interaction.guild.name}")

		if not await self.bot.actions.find_by_id(self.member.id):
			await self.bot.actions.insert(default_action_item)
		else:
			dataset = await self.bot.actions.find_by_id(self.member.id)
			dataset['actions'].append(singular_action_item)
			await self.bot.actions.update_by_id(dataset)

class RuleSelectionMenu(discord.ui.View):
	def __init__(self, member, options: list, bot, selectedAction: str=None):
		super().__init__(timeout=None)
		self.value = None
		self.member = member

		self.add_item(RuleDropdown(self.member, options, bot, selectedAction))

class CustomModerate(discord.ui.Select):
	def __init__(self, member, bot, options: list, limit=1):
		self.member = member
		self.bot = bot
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		super().__init__(placeholder='Select Moderation Action', min_values=1, max_values=limit, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
		else:
			self.view.value = self.values

		options = []
		for index, (rule, description) in enumerate(optionsDict.items(), start=1):
			rule_info = optionsDict.get(rule)
			option = discord.SelectOption(label=f"Rule {rule}", value=index, description=rule_info["description"])
			options.append(option)

		view = RuleSelectionMenu(self.member, options, self.bot, self.view.value)

		selectRule = discord.Embed(title="Moderate User", description="Please select the rule(s) the user has violated", color=discord.Color.dark_blue())
		selectRule.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		await interaction.edit_original_response(embed=selectRule, view=view)

class CustomModerateMenu(discord.ui.View):
	def __init__(self, member, options: list, bot):
		super().__init__(timeout=None)
		self.value = None
		self.member = member
		self.bot = bot

		self.add_item(CustomModerate(self.member, self.bot, options))