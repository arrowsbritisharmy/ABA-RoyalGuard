import discord
from discord.ext import commands

from utils.utils import createTicket
from utils.utils import get_admin_level
from menus import CloseTicket, CustomEscalateMenu

class Tickets(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(
		name="report",
		description="report",
		extras={"category": "Tickets", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True,
	)
	async def report(self, ctx: commands.Context):
		if not ctx.message.reference:
			invalidCommandUsage = discord.Embed(title="Warning - Invalid Command Usage", description="Please reply to a message using this command to report the message", color = discord.Color.dark_gold())
			invalidCommandUsage.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=invalidCommandUsage)
	
		await createTicket(self.bot, ctx, 12)

	@commands.hybrid_group(
		name='tickets',
		extras={"category": "Tickets", "levelPermissionNeeded": 1},
		with_app_command=True
	)
	async def tickets(self, ctx):
		pass

	@tickets.command(
		name='escalate',
		description='Escalate the ticket',
		usage="/tickets escalate",
		extras={"category": "Tickets", "levelPermissionNeeded": 1, "ignoreDefer": True},
		with_app_command=True,
		enabled=True
	)
	async def tickets_escalate(self, ctx: commands.Context):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

		if not ctx.channel.topic or not ctx.channel.topic.split(":")[0] in ["otherReport", "contentReport"]:
			insufficientPermissions = discord.Embed(
				title="Warning - Not a Ticket",
				description="This command is limited to tickets!",
				color=discord.Color.dark_gold(),
			)
			insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=insufficientPermissions)
		
		if not "-" in ctx.channel.topic:
			notClaimed = discord.Embed(
				title="Ticket Escalate",
				description="Please claim the ticket and find out more before escalating it.",
				color=discord.Color.dark_gold(),
			)
			notClaimed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=notClaimed)

		ticketCreatorID, ticketClaimerID = ctx.channel.topic.split("-")
		ticketCreatorID = int(ticketCreatorID.split(":")[1])

		ticketEscalatedRole = None
		if "/" in ticketClaimerID:
			ticketEscalatedRole = ctx.guild.get_role(int(ticketClaimerID.split("/")[-1]))
			ticketClaimerID = int(ticketClaimerID.split("/")[0])
		else:
			ticketClaimerID = int(ticketClaimerID)

		claimingMod = (
			ticketClaimerID == ctx.author.id
			or (ticketEscalatedRole and ticketEscalatedRole in ctx.author.roles)
			or userAdminLevel >= 4
		)

		if not claimingMod:
			insufficientPermissions = discord.Embed(
				title="Warning - Insufficient Permissions",
				description="You are not the user who claimed this ticket",
				color=discord.Color.dark_gold(),
			)
			insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=insufficientPermissions, ephemeral=True)

		escalateTicket = discord.Embed(
			title="Escalate Ticket",
			description="Please select the roles you wish to escalate this ticket to.",
			color=discord.Color.dark_blue()
		)
		escalateTicket.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		
		options = [
			discord.SelectOption(label="Moderator", value="moderator"),
			discord.SelectOption(label="Administrator", value="administrator"),
			discord.SelectOption(label="Tester Team", value="tester"),
			discord.SelectOption(label="Developer", value="developer"),
			discord.SelectOption(label="Special Investigation Branch", value="sib"),
			discord.SelectOption(label="Chiefs Of Staff", value="cos"),
		]

		await ctx.send(embed=escalateTicket, view=CustomEscalateMenu(bot, ctx.author.id, options), ephemeral=True)

	@tickets.command(
		name='close',
		description='Close the ticket',
		usage="/tickets close",
		extras={"category": "Tickets", "levelPermissionNeeded": 1},
		with_app_command=True,
		enabled=True
	)
	async def tickets_close(self, ctx: commands.Context):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

		if ctx.channel.topic and ctx.channel.topic.split(":")[0] == "otherReport" or ctx.channel.topic.split(":")[0] == "contentReport":
			if "-" in ctx.channel.topic:
				ticketCreatorID, ticketClaimerID = ctx.channel.topic.split("-")
				ticketCreatorID = int(ticketCreatorID.split(":")[1])

				ticketEscalatedRole = None
				if "/" in ticketClaimerID:
					ticketEscalatedRole = ctx.guild.get_role(int(ticketClaimerID.split("/")[-1]))
					ticketClaimerID = int(ticketClaimerID.split("/")[0])
				else:
					ticketClaimerID = int(ticketClaimerID)

				ticketCreator = await bot.fetch_user(ticketCreatorID)

				claimingMod = (
					ticketClaimerID == ctx.author.id
					or (ticketEscalatedRole and ticketEscalatedRole in ctx.author.roles)
					or userAdminLevel >= 4
				)

				if not claimingMod:
					insufficientPermissions = discord.Embed(
						title="Warning - Insufficient Permissions",
						description="You are not the user who claimed this ticket",
						color=discord.Color.dark_gold(),
					)
					insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					return await ctx.send(embed=insufficientPermissions, ephemeral=True)

				ticketsClose = discord.Embed(
					title="Ticket Close",
					description="Are you sure you want to close this ticket?",
					color=discord.Color.dark_blue()
				)
				ticketsClose.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				view = CloseTicket(ctx.author.id)
				await ctx.send(embed=ticketsClose, view=view)
				timeout = await view.wait()
				if timeout:
					return

				if view.value is True:
					await ctx.channel.delete()

					ticketLogs = bot.get_channel(1106921982659940403)

					ticketLog = discord.Embed(title="Ticket Closed", description=f"Ticket {ctx.channel.name} has been closed and resolved by {ctx.author.mention}.\n\nTicket is opened by {ticketCreator.mention}", color=discord.Color.dark_blue())
					ticketLog.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					await ticketLogs.send(embed=ticketLog)

					DM_resolved = discord.Embed(title="Ticket Resolved", description=f"You have successfully resolved and closed the ticket", color=discord.Color.dark_blue())
					DM_resolved.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

					DM_closed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been resolved and closed by our support team", color=discord.Color.dark_blue())
					DM_closed.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)

					try:
						await ticketCreator.send(embed=DM_closed)
					except:
						pass
					try:
						await ctx.author.send(embed=DM_resolved)
					except:
						pass
			else:
				if userAdminLevel >= 4:
					ticketsClose = discord.Embed(
						title="Ticket Close",
						description="Are you sure you want to close this ticket?",
						color=discord.Color.dark_blue()
					)
					ticketsClose.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					view = CloseTicket(ctx.author.id)
					await ctx.send(embed=ticketsClose, view=view)
					timeout = await view.wait()
					if timeout:
						return

					if view.value is True:
						ticketCreatorID = int(ctx.channel.topic.split(":")[1])
						ticketCreator = await bot.fetch_user(ticketCreatorID)

						await ctx.channel.delete()
							
						ticketLogs = bot.get_channel(1106921982659940403)

						ticketLog = discord.Embed(title="Ticket Closed", description=f"Ticket {ctx.channel.name} has been closed and resolved by {ctx.author.mention}.\n\nTicket is opened by {ticketCreator.mention}", color=discord.Color.dark_blue())
						ticketLog.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
						await ticketLogs.send(embed=ticketLog)

						DM_resolved = discord.Embed(title="Ticket Resolved", description=f"You have successfully resolved and closed the ticket", color=discord.Color.dark_blue())
						DM_resolved.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

						DM_closed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been force closed by our support team", color=0x202225)
						DM_closed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

						try:
							await ticketCreator.send(embed=DM_closed)
						except:
							pass
						try:
							await ctx.author.send(embed=DM_resolved)
						except:
							pass
				else:  
					notClaimed = discord.Embed(
						title="Ticket Close",
						description="Please claim the ticket and find out more before deleting it.",
						color=discord.Color.dark_gold(),
					)
					notClaimed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
					await ctx.send(embed=notClaimed)
		elif ctx.channel.name.startswith("verify-t"):
			await ctx.channel.delete()

			ticketCreator = await bot.fetch_user(int(ctx.channel.topic))

			ticketLogs = bot.get_channel(1106921982659940403)

			ticketLog = discord.Embed(title="Ticket Closed", description=f"Ticket {ctx.channel.name} has been closed and resolved by {ctx.author.mention}.\n\nTicket is opened by {ticketCreator.mention}", color=discord.Color.dark_blue())
			ticketLog.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ticketLogs.send(embed=ticketLog)
			
			DM_resolved = discord.Embed(title="Ticket Resolved", description=f"You have successfully resolved and closed the ticket", color=discord.Color.dark_blue())
			DM_resolved.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

			DM_closed = discord.Embed(title="Ticket Closed", description=f"Your ticket has been resolved and closed by our support team", color=discord.Color.dark_blue())
			DM_closed.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)

			try:
				await ticketCreator.send(embed=DM_closed)
			except:
				pass
		else:
			insufficientPermissions = discord.Embed(
				title = "Warning - Not a Ticket",
				description= "This command is limited to tickets!",
				color = discord.Color.dark_gold(), 
			)
			insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			await ctx.send(embed=insufficientPermissions)

	@commands.command(
		name="veteranverify",
		description="veteranverify",
		extras={"category": "Tickets", "levelPermissionNeeded": 0},
		with_app_command=False,
		enabled=True,
	)
	async def veteranverify(self, ctx: commands.Context):
		await createTicket(self.bot, ctx, 13)

async def setup(bot):
	await bot.add_cog(Tickets(bot))
