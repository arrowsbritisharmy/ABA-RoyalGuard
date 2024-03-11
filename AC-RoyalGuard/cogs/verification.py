import discord
from discord.ext import commands
from discord import app_commands

from utils.utils import client
from utils.utils import TRELLO_API_KEY
from utils.utils import TRELLO_API_TOKEN
import requests
import asyncio
from utils.utils import update_member, get_valid_ranks, get_admin_level
from menus import CustomRankbindsMenu
from typing import Union
import time

class Verification(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(
		name="check",
		description="check",
		extras={"category": "Verification", "levelPermissionNeeded": 4},
		with_app_command=False,
		enabled=True
	)
	async def check(self, ctx: commands.Context, username):
		bot = self.bot
		userToCheck = await client.get_user_by_username(username, expand=True)

		dataset = await bot.roblox.find_by_roblox(userToCheck.id)

		if len(dataset) == 0:
			RBLXaccountcheck = discord.Embed(
				title="ROBLOX Account Not Verified",
				description=f"The ROBLOX account is not verified on our database",
				color=0xff0000,
			)
			return await ctx.send(embed=RBLXaccountcheck)
		
		RBLXaccountcheck = discord.Embed(title="ROBLOX Account Check Results", color=0xff0000)
		linkedAccounts = []

		for item in dataset:
			dataset = await bot.roblox.find_by_id(item['_id'])
		
			if dataset:
				userCheckedDiscord = await bot.fetch_user(dataset['_id'])

				guild = await bot.fetch_guild(ctx.guild.id)
			
				try:
					userCheckedDiscordGuild = await guild.fetch_member(dataset['_id'])
					nickname = userCheckedDiscordGuild.nick

					if nickname == None:
						nickname = "User is not cached"
				except:
					nickname = "User is not cached"

				linkedAccounts.append(f"{userCheckedDiscord.mention} | {nickname}\n- Banned : {dataset['banned']}\n- Suspended : {dataset['suspended']}")

		RBLXaccountcheck.description = "\n\n".join(linkedAccounts)
		await ctx.send(embed=RBLXaccountcheck)

	@commands.command(
		name="transfer",
		description="transfer",
		extras={"category": "Verification", "levelPermissionNeeded": 4},
		with_app_command=False,
		enabled=True
	)
	async def transfer(self, ctx: commands.Context, member: discord.Member, username):
		bot = self.bot
		if not ctx.channel.name.startswith("dstransfer"):
			invalidChannel = discord.Embed(title="Invalid Channel", description="This command can only be run in report tickets when dealing with a verification transfer issue.", color=0xff0000)
			return await ctx.send(embed=invalidChannel)

		transferLogChannel = self.bot.get_channel(1069671688796651581)
		transferLog = discord.Embed(title="Verification Request Logs", description=f"Status : `VERIFICATION REQUEST STARTED`\nStarted by : {ctx.message.author.mention} | {ctx.message.author.id} | {ctx.message.author.display_name}\n ROBLOX Username : `{username}`\nDiscord User : {member.mention} | `{member.id}`", color=0x1d9cf3)
		await transferLogChannel.send(embed=transferLog)

		channel = ctx.channel

		def authorCheck(m):
			return m.author == member and m.channel == channel

		userToCheck = await client.get_user_by_username(username, expand=True)

		TRELLO_LIST_ID = "644569fed76bf48e8c67269f"

		url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
		response = requests.get(url)
		data = response.json()
		for user in data:
			if int(user['name'].split(":")[0]) == member.id:
				url = f"https://api.trello.com/1/cards/{user['id']}?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
				response = requests.delete(url)

		card_name = f"{member.id}:{userToCheck.id}:{member.name}:{member.discriminator}"

		url = f'https://api.trello.com/1/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}&idList={TRELLO_LIST_ID}&name={card_name}'
		response = requests.post(url)

		verifyOwnership = discord.Embed(title="Verification System 1.0", description=f"Please join this game to complete verification.\n\nhttps://www.roblox.com/games/11722765504/Verification\n\nReply with `DONE` once you have verified in the ROBLOX game.", color=discord.Color.blue())
		verifyOwnership.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=self.bot.user.avatar.url)
		await channel.send(f"Hello {member.mention}", embed=verifyOwnership)
		response = await self.bot.wait_for("message", check=authorCheck)

		async def transferMain(responseContent):
			if responseContent.upper() == "DONE":
				verifyingUser = discord.Embed(title="Verification System 1.0", description=f"Verifying user..", color=discord.Color.blue())
				await channel.send(f"Hello {member.mention}", embed=verifyingUser)
				await asyncio.sleep(1)
				url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
				response = requests.get(url)
				data = response.json()
				notVerified = False
				for user in data:
					if int(user['name'].split(":")[0]) == member.id:
						notVerified = True
						break
				if notVerified == False:
					successfullyVerified = discord.Embed(title="Verification System 1.0", description=f"Successfully verified your ROBLOX account.\n\nThis ticket will be closed momentarily.", color=0x7efc00)
					await channel.send(f"Hello {member.mention}", embed=successfullyVerified)

					default_roblox_item = {
						'_id': member.id,
						'roblox': userToCheck.id,
						'banned': False,
						'suspended': False
					}
					try:
						await self.bot.roblox.delete_by_id(member.id)
					except:
						pass
					await self.bot.roblox.insert(default_roblox_item)
					await update_member(bot, member, ctx.guild)
					await asyncio.sleep(3)
					await channel.delete()
				else:
					confirmationOfAccount = discord.Embed(title="Verification System 1.0", description=f"Please join the ROBLOX game to verify; you have not verified yourself on the game yet", color=0xd30013)
					await channel.send(f"Hello {member.mention}", embed=confirmationOfAccount)
					response = await self.bot.wait_for("message", check=authorCheck)
					await transferMain(response.content)
			elif responseContent.lower() == "cancel":
				cancelled = discord.Embed(title="Verification System 1.0", description=f"Verification procedures canceled.\n\nThis ticket will be closed momentarily.", color=0xd30013)
				await channel.send(f"Hello {member.mention}", embed=cancelled)
				await asyncio.sleep(3)
				await channel.delete()
			else:
				response = await self.bot.wait_for("message", check=authorCheck)
				await transferMain(response.content)

		await transferMain(response.content)

	@commands.command(
		name="lockserver",
		description="lockserver",
		extras={"category": "Verification", "levelPermissionNeeded": 6},
		with_app_command=False,
		enabled=True
	)
	async def lockserver(self, ctx: commands.Context):
		bot = self.bot
		rankbinds = []
		locked = True
		dataset = await bot.rankbinds.find_by_id(ctx.guild.id)
		if dataset:
			rankbinds = dataset['rankbinds']
			if dataset['locked'] == True:
				locked = False
			else:
				locked = True

		rankbindItem = {
			'_id': ctx.guild.id,
			'locked': locked,
			'rankbinds': rankbinds
		}
		await bot.rankbinds.upsert(rankbindItem)

		if locked == True:
			lockedServer = discord.Embed(title="Server Locked", description="This server is now locked. Only members with the access pass role can join", color=discord.Color.dark_blue())
			lockedServer.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=lockedServer)
		else:
			unlockedServer = discord.Embed(title="Server Unlocked", description="This server is now unlocked. Everyone can join this server now", color=discord.Color.dark_blue())
			unlockedServer.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=unlockedServer)

	@commands.hybrid_group(
		name='rankbinds',
		description="View, add or delete server rank binds",
		extras={"category": "Verification", "levelPermissionNeeded": 6},
		with_app_command=True
	)
	async def rankbinds(self, ctx):
		pass

	@rankbinds.command(
		name='add',
		description='Add a new rank bind to the server.',
		usage="/rankbinds add {group_id} {rank_ids} {nickname_template} {nickname_priority} {role} {access_pass}",
		extras={"category": "Verification", "levelPermissionNeeded": 6},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(group_id="The ID of the group you wish to bind to")
	@app_commands.describe(rank_ids="The ID(s) of the rank you wish to bind to")
	@app_commands.describe(nickname_template="The nickname template you wish to bind to")
	@app_commands.describe(nickname_priority="The nickname priority you wish to bind to")
	@app_commands.describe(role="The discord role you wish to bind this rank to")
	@app_commands.describe(access_pass="Input true if you wish to set this rankbind as an access pass to this server.")
	async def rankbinds_add(self, ctx: commands.Context, group_id: int, rank_ids, nickname_template, nickname_priority: int=0, role: discord.Role=None, access_pass: bool=False):
		bot = self.bot
		if role == None:
			roleID = None
			roleMention = None
		elif role != None:
			roleID = role.id
			roleMention = role.mention

		if "-" in rank_ids:
			rank_start, rank_end = map(int, rank_ids.split("-"))
		else:
			rank_start = rank_end = int(rank_ids)

		valid_ranks = await get_valid_ranks(group_id)

		newRankbind = discord.Embed(
			title="New Rankbind", 
			color=discord.Color.dark_blue(),
			)
		newRankbind.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		rankbindsAdded = 0
		rankbindsUpdated = 0

		for rank_id in range(rank_start, rank_end+1):
			if rank_id in valid_ranks:
				newRankbind.add_field(
					name=f"Rank {rank_id}",
					value=f"Nickname Template : `{nickname_template}`\nNickname Priority : {nickname_priority}\nRoles Binded : {roleMention}\nAccess Pass : {str(access_pass).lower()}",
					inline=True
				)

				dataset = await bot.rankbinds.find_by_id(ctx.guild.id)
				if dataset:
					found = False
					for rankbind in dataset['rankbinds']:
						if rankbind['group_id'] == group_id and rankbind['rank_id'] == rank_id:
							rankbindsUpdated += 1

							rankbind['nickname_template'] = nickname_template
							rankbind['nickname_priority'] = nickname_priority
							rankbind['access_pass'] = access_pass
							rankbind['role'] = [roleID]
							await bot.rankbinds.update_by_id(dataset)
							found = True
							break
					if found == True:
						continue

				rankbindsAdded += 1

				default_rankbind_item = {
					'_id': ctx.guild.id,
					'locked': False,
					'rankbinds': [{
						'group_id': group_id,
						"rank_id": rank_id,
						"nickname_template": nickname_template,
						"nickname_priority": nickname_priority,
						"role": [roleID],
						"access_pass": access_pass
						}]
				}

				singular_rankbind_item = {
						'group_id': group_id,
							"rank_id": rank_id,
							"nickname_template": nickname_template,
							"nickname_priority": nickname_priority,
							"role": [roleID],
							"access_pass": access_pass
					}

				if not await bot.rankbinds.find_by_id(ctx.guild.id):
					await bot.rankbinds.insert(default_rankbind_item)
				else:
					dataset = await bot.rankbinds.find_by_id(ctx.guild.id)
					dataset['rankbinds'].append(singular_rankbind_item)
					await bot.rankbinds.update_by_id(dataset)

		if rankbindsAdded == 0 and rankbindsUpdated == 0:
			noRankbindsAdded = discord.Embed(title="Warning - Invalid Arguments", description=f"There are no rank id(s) `{rank_ids}`", color=discord.Color.dark_gold())
			noRankbindsAdded.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=noRankbindsAdded)

		newRankbind.description = f"Added {rankbindsAdded} rankbinds and updated {rankbindsUpdated} rankbinds"
		await ctx.send(embed=newRankbind)

	@rankbinds.command(
		name='delete',
		description='Delete an existing rank bind from the server.',
		usage="/rankbinds delete {group_id} {rank_ids}",
		extras={"category": "Verification", "levelPermissionNeeded": 6},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(group_id="The ID of the group the rank bind is associated with.")
	@app_commands.describe(rank_ids="The ID(s) of the rank bind you wish to delete.")
	async def rankbinds_delete(self, ctx: commands.Context, group_id: int, rank_ids):
		bot = self.bot
		if "-" in rank_ids:
			rank_start, rank_end = map(int, rank_ids.split("-"))
		else:
			rank_start = rank_end = int(rank_ids)

		valid_ranks = await get_valid_ranks(group_id)

		rankbindsDeleted = 0

		for rank_id in range(rank_start, rank_end + 1):
			if rank_id in valid_ranks:
				dataset = await bot.rankbinds.find_by_id(ctx.guild.id)
				if dataset:
					for rankbind in dataset['rankbinds']:
						if rankbind['group_id'] == group_id and rankbind['rank_id'] == rank_id:
							dataset['rankbinds'].remove(rankbind)
							await bot.rankbinds.upsert(dataset)
							rankbindsDeleted += 1

		if rankbindsDeleted == 0:
			no_rankbinds_deleted_message = discord.Embed(title="Warning - Invalid Arguments",
														description=f"There are no rank id(s) `{rank_ids}`",
														color=discord.Color.dark_gold())
			no_rankbinds_deleted_message.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=no_rankbinds_deleted_message)
		else:
			deleted_rankbind_message = discord.Embed(title="Rankbinds Deleted",
													description=f"Successfully deleted `{rankbindsDeleted}` rankbinds",
													color=discord.Color.dark_blue())
			deleted_rankbind_message.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=deleted_rankbind_message)

	@rankbinds.command(
		name='edit',
		description='Edits an existing rank bind from the server',
		usage="/rankbinds edit {group_id} {rank_ids} {nickname_priority} {nickname_template} {add_role} {remove_role} {access_pass}",
		extras={"category": "Verification", "levelPermissionNeeded": 6},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(group_id="The ID of the group you wish to edit.")
	@app_commands.describe(rank_ids="The ID(s) of the rank you wish to edit.")
	@app_commands.describe(nickname_priority="Edit the nickname priority of the rank bind")
	@app_commands.describe(nickname_template="Edit the nickname template of the rank bind")
	@app_commands.describe(add_role="Add a new discord role to the rank bind")
	@app_commands.describe(remove_role="Removes an existing binded discord role from the rank bind")
	@app_commands.describe(access_pass="Edit the access pass of the rank bind")
	async def rankbinds_edit(self, ctx: commands.Context, group_id: int, rank_ids, nickname_priority: int=None, nickname_template: str=None, add_role: discord.Role=None, remove_role: discord.Role=None, access_pass: bool=None):
		bot = self.bot
		if "-" in rank_ids:
			rank_start, rank_end = map(int, rank_ids.split("-"))
		else:
			rank_start = rank_end = int(rank_ids)

		valid_ranks = await get_valid_ranks(group_id)

		rankbindsEdited = 0

		for rank_id in range(rank_start, rank_end + 1):
			if rank_id in valid_ranks:
				dataset = await bot.rankbinds.find_by_id(ctx.guild.id)
				if dataset:
					for rankbind in dataset['rankbinds']:
						if rankbind['group_id'] == group_id and rankbind['rank_id'] == rank_id:
							if nickname_template is not None:
								rankbind['nickname_template'] = nickname_template
							if nickname_priority is not None:
								rankbind['nickname_priority'] = nickname_priority
							if access_pass is not None:
								rankbind['access_pass'] = access_pass
							if add_role is not None:
								rankbind['role'].append(add_role.id)
							if remove_role is not None:
								rankbind['role'].remove(remove_role.id)
							await bot.rankbinds.update_by_id(dataset)
							rankbindsEdited += 1

		if rankbindsEdited == 0:
			no_rankbinds_deleted_message = discord.Embed(title="Warning - Invalid Arguments", description=f"There are no rank id(s) `{rank_ids}`", color=discord.Color.dark_gold())
			no_rankbinds_deleted_message.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=no_rankbinds_deleted_message)
		else:
			updatedRankbind = discord.Embed(title="Rankbinks Updated", description=f"Successfully updated `{rankbindsEdited}` rankbinds", color=discord.Color.dark_blue())
			updatedRankbind.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=updatedRankbind)

	@rankbinds.command(
		name='view',
		description='Lists all the rank bind(s) in the server.',
		usage="/rankbinds view",
		extras={"category": "Verification", "levelPermissionNeeded": 6},
		with_app_command=True,
		enabled=True
	)
	async def rankbinds_view(self, ctx: commands.Context):
		bot = self.bot
		dataset = await bot.rankbinds.find_by_id(ctx.guild.id)

		if not dataset:
			noRankbindsFound = discord.Embed(title="Warning - No Rankbind Entries", description="There are no rank binds found", color = discord.Color.dark_gold())
			noRankbindsFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=noRankbindsFound)

		try:
			rankbinds = dataset['rankbinds']
			rankbindGroups = set()

			for rankbind in rankbinds:
				rankbindGroups.add(rankbind["group_id"])

			options = []
			for group in rankbindGroups:
				options.append(
					discord.SelectOption(
						label=group,
						description=f"View the rankbinds linked to group {group}",
						value=group,
					)
				)

			selectGroupToView = discord.Embed(title=f"Viewing Rankbinds For {ctx.guild.name}", description="Select the group you wish to view rankbinds linked to.", color=discord.Color.dark_blue())
			selectGroupToView.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			view = CustomRankbindsMenu(ctx.author.id, options, bot)
			await ctx.send(embed=selectGroupToView, view=view)
		except:
			noRankbindsFound = discord.Embed(title="Warning - No Rankbind Entries", description="There are no rank binds found", color = discord.Color.dark_gold())
			noRankbindsFound.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=noRankbindsFound)
		
	@commands.command(
		name="verify",
		description="verify",
		extras={"category": "Verification", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=False
	)
	async def verify(self, ctx: discord.Interaction):
		bot = self.bot
		category = discord.utils.get(ctx.guild.categories, id=1091254685412905031)

		for channel in category.channels:
			if isinstance(channel, discord.TextChannel):
				if str(ctx.user.id) in channel.topic:
					openTicket = discord.Embed(title="Verify Ticket", description=f"There is already an open ticket at {channel.mention}", color=discord.Color.dark_blue())
					openTicket.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
					return await ctx.followup.send(embed=openTicket, ephemeral=True)

		def authorCheck(m):
			return m.author == ctx.user and m.channel == channel
		
		ticket_number = 1
		ticketType = "verify-t"

		for channel in category.channels:
			if isinstance(channel, discord.TextChannel):
				if channel.name.split('-')[0] == ticketType:
					ticket_number += 1

		name = f"{ticketType}-{ticket_number}"

		support = ctx.guild.get_role(1069672694175506463)
		moderator = ctx.guild.get_role(1069674122642206771)
		administrator = ctx.guild.get_role(1069667659563683850)
		chiefsofstaff = ctx.guild.get_role(1069664070921363596)
		op = ctx.guild.get_role(1069663160384106608)
		
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ctx.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					support: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					moderator: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					administrator: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					chiefsofstaff: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					op: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=ctx.user.id, overwrites = overwrites, category=category)

		ticketCreated = discord.Embed(title="Verify Ticket", description=f"Your verify ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
		ticketCreated.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
		await ctx.followup.send(embed=ticketCreated, ephemeral=True)

		dataset = await bot.roblox.find_by_id(ctx.user.id)
		if dataset:
			alreadyVerified = discord.Embed(title="Verification System 4.0", description=f"You're already verified.\n\nThis ticket will be closed momentarily.", color=0xd30013)
			await channel.send(f"Hello {ctx.user.mention}", embed=alreadyVerified)
			await asyncio.sleep(5)
			await channel.delete()

		async def usernameInput(sendStartMessage=False):
			if sendStartMessage:
				RBLXusernameinput = discord.Embed(title="Verification System 4.0", description=f"What is your ROBLOX username?", color=discord.Color.blue())
				RBLXusernameinput.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
				await channel.send(f"Hello {ctx.user.mention}", embed=RBLXusernameinput)

			response = await bot.wait_for("message", check=authorCheck)

			if response.content.lower() == "cancel":
				cancelled = discord.Embed(title="Verification System 4.0", description=f"Verification procedures cancelled.\n\nThis ticket will be closed momentarily.", color=0xd30013)
				await channel.send(f"Hello {ctx.user.mention}", embed=cancelled)
				await asyncio.sleep(3)
				await channel.delete()

			RBLXusername = response.content
			
			retrievingDetails = discord.Embed(title="Verification System 4.0", description=f"Retrieving details from ROBLOX..", color=discord.Color.blue())
			retrievingDetails.set_footer(text=f"Royal Guard 2022", icon_url=bot.user.avatar.url)
			await channel.send(f"Hello {ctx.user.mention}", embed=retrievingDetails)
			await asyncio.sleep(1)

			try:
				user = await client.get_user_by_username(RBLXusername, expand=True)
				robloxID = user.id
				confirmationOfAccount = discord.Embed(title="Verification System 4.0", description=f"Is this your ROBLOX account?\n\nUsername : [{user.name}](https://www.roblox.com/users/{user.id}/profile)\nROBLOX Profile : https://www.roblox.com/users/{user.id}/profile\n\nPlease reply with **\"YES\"** or **\"NO\"**", color=discord.Color.blue())
				confirmationOfAccount.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
				await channel.send(f"Hello {ctx.user.mention}", embed=confirmationOfAccount)
				response = await bot.wait_for("message", check=authorCheck)
			except:
				confirmationOfAccount = discord.Embed(title="Verification System 4.0", description=f"The ROBLOX account username you have entered does not exist.\n\nPlease try again.", color=0xd30013)
				confirmationOfAccount.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
				await channel.send(f"Hello {ctx.user.mention}", embed=confirmationOfAccount)
				await usernameInput()

			async def checkIfAccount(responseContent):
				if responseContent.upper() == "YES":
					dataset = await bot.roblox.find_by_roblox(robloxID)
					if len(dataset) >= 1:
						accountAlreadyExists = discord.Embed(title="Verification System 4.0", description=f"The ROBLOX account has been verified on our database already. Make a report ticket using the command `!report` and provide a **valid** reason to Alfie to make a verification transfer request.", color=0xd30013)
						accountAlreadyExists.set_footer(text=f"This ticket will be closed momentarily", icon_url=bot.user.avatar.url)
						await channel.send(f"Hello {ctx.user.mention}", embed=accountAlreadyExists)
						await asyncio.sleep(3)
						await channel.delete()
					else:
						TRELLO_LIST_ID = "644569fed76bf48e8c67269f"

						url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
						response = requests.get(url)
						data = response.json()
						for user in data:
							if int(user['name'].split(":")[0]) == ctx.user.id:
								url = f"https://api.trello.com/1/cards/{user['id']}?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
								response = requests.delete(url)

						card_name = f"{ctx.user.id}:{robloxID}:{ctx.user.name}:{ctx.user.discriminator}"

						url = f'https://api.trello.com/1/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}&idList={TRELLO_LIST_ID}&name={card_name}'
						response = requests.post(url)
						verifyOwnership = discord.Embed(title="Verification System 4.0", description=f"Please join this game to complete verification.\n\nhttps://www.roblox.com/games/11722765504/Verification\n\nReply with `DONE` once you have verified in the ROBLOX game.", color=discord.Color.blue())
						verifyOwnership.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
						await channel.send(f"Hello {ctx.user.mention}", embed=verifyOwnership)
						response = await bot.wait_for("message", check=authorCheck)
						
						async def accountCheck(responseContent):
							if responseContent.upper() == "DONE":
								verifyingUser = discord.Embed(title="Verification System 4.0", description=f"Verifying user..", color=discord.Color.blue())
								await channel.send(f"Hello {ctx.user.mention}", embed=verifyingUser)
								await asyncio.sleep(1)
								url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
								response = requests.get(url)
								data = response.json()
								notVerified = False
								for user in data:
									if int(user['name'].split(":")[0]) == ctx.user.id:
										notVerified = True
										break
								if notVerified == False:
									successfullyVerified = discord.Embed(title="Verification System 4.0", description=f"Successfully verified your ROBLOX account.\n\nThis ticket will be closed momentarily.", color=0x7efc00)
									await channel.send(f"Hello {ctx.user.mention}", embed=successfullyVerified)
									default_roblox_item = {
										'_id': ctx.user.id,
										'roblox': robloxID,
										'banned': False,
										'suspended': False,
									}
									await bot.roblox.insert(default_roblox_item)
									await update_member(ctx.user, ctx.guild)
									await asyncio.sleep(3)
									await channel.delete()
								else:
									confirmationOfAccount = discord.Embed(title="Verification System 4.0", description=f"Please join the ROBLOX game to verify, you have not verified yourself on the game yet", color=0xd30013)
									await channel.send(f"Hello {ctx.user.mention}", embed=confirmationOfAccount)
									response = await bot.wait_for("message", check=authorCheck)
									await accountCheck(response.content)
							elif responseContent.lower() == "cancel":
								cancelled = discord.Embed(title="Verification System 4.0", description=f"Verification procedures cancelled.\n\nThis ticket will be closed momentarily.", color=0xd30013)
								await channel.send(f"Hello {ctx.user.mention}", embed=cancelled)
								await asyncio.sleep(3)
								await channel.delete()
							else:
								response = await bot.wait_for("message", check=authorCheck)
								await accountCheck(response.content)
						await accountCheck(response.content)         
				elif responseContent.upper() == "NO":
					await usernameInput(True)
				elif responseContent.lower() == "cancel":
					cancelled = discord.Embed(title="Verification System 4.0", description=f"Verification procedures cancelled.\n\nThis ticket will be closed momentarily.", color=0xd30013)
					await channel.send(f"Hello {ctx.user.mention}", embed=cancelled)
					await asyncio.sleep(3)
					await channel.delete()
				else:
					response = await bot.wait_for("message", check=authorCheck)
					await checkIfAccount(response.content)

			await checkIfAccount(response.content)

		await usernameInput(True)

	@commands.command(
		name="reverify", 
		description="reverify",
		extras={"category": "Verification", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=False
	)
	async def reverify(self, ctx: discord.Interaction):
		bot = self.bot
		category = discord.utils.get(ctx.guild.categories, id=1091254685412905031)

		for channel in category.channels:
			if isinstance(channel, discord.TextChannel):
				if str(ctx.user.id) in channel.topic:
					openTicket = discord.Embed(title="Verify Ticket", description=f"There is already an open ticket at {channel.mention}", color=discord.Color.dark_blue())
					openTicket.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
					return await ctx.followup.send(embed=openTicket, ephemeral=True)

		dataset = await bot.roblox.find_by_id(ctx.user.id)

		if not dataset:
			return

		def authorCheck(m):
			return m.author == ctx.user and m.channel == channel

		ticket_number = 1
		ticketType = "verify-t"

		for channel in category.channels:
			if isinstance(channel, discord.TextChannel):
				if channel.name.split('-')[0] == ticketType:
					ticket_number += 1

		name = f"{ticketType}-{ticket_number}"
		
		support = ctx.guild.get_role(1069672694175506463)
		moderator = ctx.guild.get_role(1069674122642206771)
		administrator = ctx.guild.get_role(1069667659563683850)
		chiefsofstaff = ctx.guild.get_role(1069664070921363596)
		op = ctx.guild.get_role(1069663160384106608)
		
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ctx.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					support: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					moderator: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					administrator: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					chiefsofstaff: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
					op: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=ctx.user.id, overwrites = overwrites, category=category)

		moderator = ctx.guild.get_role(1074282158971158558)
		administrator = ctx.guild.get_role(1074282157167616010)
		
		ticketCreated = discord.Embed(title="Verify Ticket", description=f"Your verify ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
		ticketCreated.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
		await ctx.followup.send(embed=ticketCreated, ephemeral=True)

		robloxID = dataset['roblox']

		user = await client.get_user(robloxID)
		currentUsername = user.name

		async def usernameInput(sendStartMessage=False):
			async def main(RBLXusername):
				try:
					user = await client.get_user_by_username(RBLXusername, expand=True)
					robloxID = user.id
					confirmationOfAccount = discord.Embed(title="Verification System 4.0", description=f"Is this your ROBLOX account?\n\nUsername : [{user.name}](https://www.roblox.com/users/{user.id}/profile)\nROBLOX Profile : https://www.roblox.com/users/{user.id}/profile\n\nPlease reply with **\"YES\"** or **\"NO\"**", color=discord.Color.blue())
					confirmationOfAccount.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
					await channel.send(f"Hello {ctx.user.mention}", embed=confirmationOfAccount)
					response = await bot.wait_for("message", check=authorCheck)
				except:
					confirmationOfAccount = discord.Embed(title="Verification System 4.0", description=f"The ROBLOX account username you have entered does not exist.\n\nPlease try again.", color=0xd30013)
					confirmationOfAccount.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
					await channel.send(f"Hello {ctx.user.mention}", embed=confirmationOfAccount)
					await usernameInput()

				async def checkIfAccount(responseContent):
					if responseContent.upper() == "YES":
						if RBLXusername.lower() == currentUsername.lower():
							alreadyVerified = discord.Embed(title="Verification System 4.0", description=f"You're already verified.\n\nThis ticket will be closed momentarily.", color=0xd30013)
							await channel.send(f"Hello {ctx.user.mention}", embed=alreadyVerified)
							await asyncio.sleep(3)
							await channel.delete()

						dataset = await bot.roblox.find_by_roblox(robloxID)
						if len(dataset) >= 1:
							accountAlreadyExists = discord.Embed(title="Verification System 4.0", description=f"This ROBLOX account has been verified on our database already. Make a discord transfer ticket in <#1091095337214689310> via Verification Tickets -> Create Ticket -> Discord Transfer.", color=0xd30013)
							accountAlreadyExists.set_footer(text=f"This ticket will be closed momentarily", icon_url=bot.user.avatar.url)
							await channel.send(f"Hello {ctx.user.mention}", embed=accountAlreadyExists)
							await asyncio.sleep(3)
							await channel.delete()
						else:
							TRELLO_LIST_ID = "644569fed76bf48e8c67269f"

							url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
							response = requests.get(url)
							data = response.json()
							for user in data:
								if int(user['name'].split(":")[0]) == ctx.user.id:
									url = f"https://api.trello.com/1/cards/{user['id']}?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
									response = requests.delete(url)

							card_name = f"{ctx.user.id}:{robloxID}:{ctx.user.name}:{ctx.user.discriminator}"

							url = f'https://api.trello.com/1/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}&idList={TRELLO_LIST_ID}&name={card_name}'
							response = requests.post(url)
							verifyOwnership = discord.Embed(title="Verification System 4.0", description=f"Please join this game to complete verification.\n\nhttps://www.roblox.com/games/11722765504/Verification\n\nReply with `DONE` once you have verified in the ROBLOX game.", color=discord.Color.blue())
							verifyOwnership.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
							await channel.send(f"Hello {ctx.user.mention}", embed=verifyOwnership)
							response = await bot.wait_for("message", check=authorCheck)
							
							async def accountCheck(responseContent):
								if responseContent.upper() == "DONE":
									verifyingUser = discord.Embed(title="Verification System 4.0", description=f"Verifying user..", color=discord.Color.blue())
									await channel.send(f"Hello {ctx.user.mention}", embed=verifyingUser)
									await asyncio.sleep(1)
									url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
									response = requests.get(url)
									data = response.json()
									notVerified = False
									for user in data:
										if int(user['name'].split(":")[0]) == ctx.user.id:
											notVerified = True
											break
									if notVerified == False:
										successfullyVerified = discord.Embed(title="Verification System 4.0", description=f"Successfully verified your ROBLOX account.\n\nThis ticket will be closed momentarily.", color=0x7efc00)
										await channel.send(f"Hello {ctx.user.mention}", embed=successfullyVerified)
										default_roblox_item = {
											'_id': ctx.user.id,
											'roblox': robloxID,
											'banned': False,
											'suspended': False
										}
										await bot.roblox.delete_by_id(ctx.user.id)
										await bot.roblox.insert(default_roblox_item)
										await update_member(ctx.user, ctx.guild)
										await asyncio.sleep(3)
										await channel.delete()
									else:
										confirmationOfAccount = discord.Embed(title="Verification System 4.0", description=f"Please join the ROBLOX game to verify, you have not verified yourself on the game yet", color=0xd30013)
										await channel.send(f"Hello {ctx.user.mention}", embed=confirmationOfAccount)
										response = await bot.wait_for("message", check=authorCheck)
										await accountCheck(response.content)
								elif responseContent.lower() == "cancel":
									cancelled = discord.Embed(title="Verification System 4.0", description=f"Verification procedures cancelled.\n\nThis ticket will be closed momentarily.", color=0xd30013)
									await channel.send(f"Hello {ctx.user.mention}", embed=cancelled)
									await asyncio.sleep(3)
									await channel.delete()
								else:
									response = await bot.wait_for("message", check=authorCheck)
									await accountCheck(response.content)
							await accountCheck(response.content)         
					elif responseContent.upper() == "NO":
						await usernameInput(True)
					elif responseContent.lower() == "cancel":
						cancelled = discord.Embed(title="Verification System 4.0", description=f"Verification procedures cancelled.\n\nThis ticket will be closed momentarily.", color=0xd30013)
						await channel.send(f"Hello {ctx.user.mention}", embed=cancelled)
						await asyncio.sleep(3)
						await channel.delete()
					else:
						response = await bot.wait_for("message", check=authorCheck)
						await checkIfAccount(response.content)

				await checkIfAccount(response.content)

			async def validateRespond(responseContent):
				if responseContent.lower() == "cancel":
					cancelled = discord.Embed(title="Verification System 4.0", description=f"Verification procedures cancelled.\n\nThis ticket will be closed momentarily.", color=0xd30013)
					await channel.send(f"Hello {ctx.user.mention}", embed=cancelled)
					await asyncio.sleep(3)
					await channel.delete()

				RBLXusername = responseContent
				
				retrievingDetails = discord.Embed(title="Verification System 4.0", description=f"Retrieving details from ROBLOX..", color=discord.Color.blue())
				retrievingDetails.set_footer(text=f"Royal Guard 2022", icon_url=bot.user.avatar.url)
				await channel.send(f"Hello {ctx.user.mention}", embed=retrievingDetails)
				await asyncio.sleep(1)
				await main(RBLXusername)

			if sendStartMessage:
				RBLXusernameinput = discord.Embed(title="Verification System 4.0", description=f"What is your ROBLOX username?", color=discord.Color.blue())
				RBLXusernameinput.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
				await channel.send(f"Hello {ctx.user.mention}", embed=RBLXusernameinput)
				response = await bot.wait_for("message", check=authorCheck)
				await validateRespond(response.content)

			await main(user.name)

		await usernameInput()

	@commands.hybrid_command(
		name="update",
		description="Updates user roles",
		extras={"category": "Verification", "levelPermissionNeeded": 0},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(member_or_role="Updates a member or role")
	@app_commands.describe(all="Updates everyone in the server")
	async def update(self, ctx: commands.Context, member_or_role: Union[discord.Role, discord.Member] = None, all: bool = False):
		bot = self.bot
		if all != None:
			user = ctx.author
		else:
			user = ctx.user

		if all == False and member_or_role == None or all == None:
			member = user
			added_roles = []
			removed_roles = []

			added_roles, removed_roles, new_nickname = await update_member(bot, member, ctx.guild)

			roles_update = discord.Embed(title="Roles Update")

			dataset = await bot.roblox.find_by_id(member.id)
			if dataset:
				roles_update.description="Successfully updated user roles"
				roles_update.color=discord.Color.dark_blue()
			else:
				roles_update.description="User is not verified on our database"
				roles_update.color=discord.Color.dark_gold()

			added_role_list = "\n".join([f"- <@&{id}>" for id in added_roles]) if added_roles else "None"
			removed_role_list = "\n".join([f"- <@&{id}>" for id in removed_roles]) if removed_roles else "None"
			roles_update.set_author(name=member.name, icon_url=member.avatar)
			roles_update.add_field(name="Nickname", value=new_nickname or "None", inline=False)
			roles_update.add_field(name="Roles Added", value=added_role_list, inline=False)
			roles_update.add_field(name="Roles Removed", value=removed_role_list, inline=False)

			if all != None:
				await ctx.send(embed=roles_update, delete_after=20)
			else:
				return roles_update

		if all == True:
			adminLevelRequired = 6
			userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

			if not userAdminLevel >= adminLevelRequired:
				insufficientPermissions = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This `all` option of this command is limited to the admin level **{adminLevelRequired}**!", color = discord.Color.dark_gold())
				insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				return await ctx.send(embed=insufficientPermissions)

			start_time = time.monotonic()

			TotalUpdated = 0
			Updated = 0
			Ignored = 0
			NonVerified = 0

			updatingNow = discord.Embed(title="Updating Now..", description="Please hold on while we update all members in the server..", color=0x7efc00)
			await ctx.send(embed=updatingNow)
			for member in ctx.guild.members:
				if member.bot:
					Ignored += 1
					continue
				dataset = await bot.roblox.find_by_id(member.id)
				if dataset:
					try:
						await update_member(bot, member, ctx.guild)
						Updated += 1
					except:
						Ignored += 1
				else:
					try:
						await update_member(bot, member, ctx.guild)
						NonVerified += 1
					except:
						Ignored += 1

			end_time = time.monotonic()

			duration_seconds = int(end_time - start_time)

			if duration_seconds >= 3600:
				duration_hours = duration_seconds // 3600
				duration_minutes = (duration_seconds % 3600) // 60
				duration_str = f"{duration_hours} hour{'s' if duration_hours > 1 else ''}"
				if duration_minutes > 0:
					duration_str += f" {duration_minutes} minute{'s' if duration_minutes > 1 else ''}"
			else:
				duration_minutes = duration_seconds // 60
				if duration_minutes > 0:
					duration_str = f"{duration_minutes} minute{'s' if duration_minutes > 1 else ''}"
				else:
					duration_str = f"{duration_seconds} second{'s' if duration_seconds > 1 else ''}"

			TotalUpdated = Updated + Ignored + NonVerified
			updatingComplete = discord.Embed(title="Update Complete", description=f"We have finished updating all the members in this server! Here are the results!\n\nTotal Updated : {TotalUpdated}\nUpdated : {Updated}\nIgnored : {Ignored}\nNon Verified : {NonVerified}\n\nTime Taken : {duration_str}", color=0x7efc00)
			channel = ctx.channel
			await channel.send(f"Hello {ctx.author.mention}", embed=updatingComplete)

		if not member_or_role == None and all == False:
			role = discord.utils.get(ctx.guild.roles, id=member_or_role.id)
			if role:
				adminLevelRequired = 5
				userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

				if not userAdminLevel >= adminLevelRequired:
					insufficientPermissions = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This `role` option of this command is limited to the admin level **{adminLevelRequired}**!", color = discord.Color.dark_gold())
					insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					return await ctx.send(embed=insufficientPermissions)

				start_time = time.monotonic()

				TotalUpdated = 0
				Updated = 0
				Ignored = 0
				NonVerified = 0

				updatingNow = discord.Embed(title="Updating Now..", description=f"Please hold on while we update `{len(member_or_role.members)}` members in the role {member_or_role.mention}", color=discord.Color.blue())
				await ctx.send(embed=updatingNow)
				for member in member_or_role.members:
					if member.bot:
						Ignored += 1
						continue
					dataset = await bot.roblox.find_by_id(member.id)
					if dataset:
						try:
							await update_member(bot, member, ctx.guild)
							Updated += 1
						except:
							Ignored += 1
					else:
						try:
							await update_member(bot, member, ctx.guild)
							NonVerified += 1
						except:
							Ignored += 1

				end_time = time.monotonic()

				duration_seconds = int(end_time - start_time)

				if duration_seconds >= 3600:
					duration_hours = duration_seconds // 3600
					duration_minutes = (duration_seconds % 3600) // 60
					duration_str = f"{duration_hours} hour{'s' if duration_hours > 1 else ''}"
					if duration_minutes > 0:
						duration_str += f" {duration_minutes} minute{'s' if duration_minutes > 1 else ''}"
				else:
					duration_minutes = duration_seconds // 60
					if duration_minutes > 0:
						duration_str = f"{duration_minutes} minute{'s' if duration_minutes > 1 else ''}"
					else:
						duration_str = f"{duration_seconds} second{'s' if duration_seconds > 1 else ''}"

				TotalUpdated = Updated + Ignored + NonVerified
				updatingComplete = discord.Embed(title="Update Complete", description=f"We have finished updating all the members in the role {member_or_role.mention}! Here are the results!\n\nTotal Updated : {TotalUpdated}\nUpdated : {Updated}\nIgnored : {Ignored}\nNon Verified : {NonVerified}\n\nTime Taken : {duration_str}", color=0x7efc00)
				channel = ctx.channel
				await channel.send(f"Hello {ctx.author.mention}", embed=updatingComplete)
			else:
				adminLevelRequired = 2
				userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

				if not userAdminLevel >= adminLevelRequired:
					insufficientPermissions = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This `member` option of this command is limited to the admin level **{adminLevelRequired}**!", color = discord.Color.dark_gold())
					insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					return await ctx.send(embed=insufficientPermissions)

				member = member_or_role

				added_roles = []
				removed_roles = []

				added_roles, removed_roles, new_nickname = await update_member(bot, member, ctx.guild)

				roles_update = discord.Embed(title="Roles Update")

				dataset = await bot.roblox.find_by_id(member.id)
				if dataset:
					roles_update.description="Successfully updated user roles"
					roles_update.color=discord.Color.dark_blue()
				else:
					roles_update.description="User is not verified on our database"
					roles_update.color=discord.Color.dark_gold()

				added_role_list = "\n".join([f"<@&{id}>" for id in added_roles]) if added_roles else "None"
				removed_role_list = "\n".join([f"<@&{id}>" for id in removed_roles]) if removed_roles else "None"
				roles_update.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				roles_update.add_field(name="Nickname", value=new_nickname or "None", inline=False)
				roles_update.add_field(name="Roles Added", value=added_role_list, inline=False)
				roles_update.add_field(name="Roles Removed", value=removed_role_list, inline=False)

				await ctx.send(embed=roles_update, delete_after=20)

	@commands.hybrid_command(
		name="refresh",
		description="Update a user in every server",
		extras={"category": "Verification", "levelPermissionNeeded": 5},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(user="The user to update")
	async def refresh(self, ctx: commands.Context, user: discord.User):
		bot = self.bot

		updateInAllServers = discord.Embed(title="Update Roles", color=discord.Color.dark_blue())
		server_fields = {}

		for index, guild in enumerate(bot.guilds, start=1):
			field_value = "```diff\n- ❌ Awaiting Update.. ❌```"
			server_fields[guild.id] = (index, field_value)
			updateInAllServers.add_field(name=guild.name, value=field_value, inline=True)

		message = await ctx.send(embed=updateInAllServers)

		for guild_id, (field_index, field_value) in server_fields.items():
			message = await ctx.fetch_message(message.id)
			embed = message.embeds[0]

			embed.set_field_at(field_index - 1, name=embed.fields[field_index - 1].name, value="```- 🔄 Updating.. 🔄```")

			await message.edit(embed=embed)

			await update_member(bot, user, bot.get_guild(guild_id))

			embed.set_field_at(field_index - 1, name=embed.fields[field_index - 1].name, value="```diff\n+ ✅ Updated ✅```")

			await message.edit(embed=embed)

async def setup(bot):
	await bot.add_cog(Verification(bot))
