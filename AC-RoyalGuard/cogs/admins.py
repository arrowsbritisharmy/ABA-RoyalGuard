import discord
from discord.ext import commands
from discord import app_commands

from typing import Union
from utils.utils import get_admin_level

class Admins(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.hybrid_group(
		name='admins',
		extras={"category": "Admins", "levelPermissionNeeded": 0},
		with_app_command=True
	)
	async def admins(self, ctx):
		pass

	@admins.command(
		name='add',
		description='Add a new role to the level admin.',
		usage="/admins add {member_or_role} {admin_level}",
		extras={"category": "Admins", "levelPermissionNeeded": 5},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(member_or_role="The member or role you wish to assign admin to.")
	@app_commands.describe(admin_level="The level of admin you wish to assign.")
	async def admins_add(self, ctx: commands.Context, member_or_role: Union[discord.Role, discord.Member], admin_level: int):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

		role = discord.utils.get(ctx.guild.roles, id=member_or_role.id)
		adminLevelRequired = 5 if role else 7

		if not userAdminLevel >= adminLevelRequired:
			title = "Warning - Insufficient Permissions"
			description = f"The `delete` option of this command is limited to the admin level **{adminLevelRequired}**!" if role else f"The `member` option of this command is limited to the admin level **{adminLevelRequired}**!"
			insufficientPermissions = discord.Embed(title=title, description=description, color=discord.Color.dark_gold())
			insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=insufficientPermissions)

		addAdmins = discord.Embed(
			title="Admin Level Added",
			description=f"Successfully added level admin {admin_level} to {member_or_role.mention}",
			color=discord.Color.dark_blue()
		)
		addAdmins.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		default_admin_item = {
			'_id': ctx.guild.id,
			'admins': [{
				"levelPermissionNeeded": admin_level,
				"MemberOrRole": member_or_role.id,
				"Server": ctx.guild.id,
			}]
		}

		singular_admin_item = {
			'AdminLevel': admin_level,
			"MemberOrRole": member_or_role.id,
			"Server": ctx.guild.id,
		}

		if not await bot.admins.find_by_id(ctx.guild.id):
			await bot.admins.insert(default_admin_item)
		else:
			dataset = await bot.admins.find_by_id(ctx.guild.id)
			admins = dataset['admins']
			if any(admin['MemberOrRole'] == member_or_role.id for admin in admins):
				title = "Warning - Admin Level Found"
				description = "This user or role already has an assigned level admin, if you wish to change it, please delete using `/admins delete` and re-add it."
				alreadyAdmin = discord.Embed(title=title, description=description, color=discord.Color.dark_gold())
				alreadyAdmin.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
				return await ctx.send(embed=alreadyAdmin)
			else:
				admins.append(singular_admin_item)
				await bot.admins.update_by_id(dataset)

		await ctx.send(embed=addAdmins)

	@admins.command(
		name='delete',
		description='Delete a role from the level admin.',
		usage="/admins delete {member_or_role}",
		extras={"category": "Admins", "levelPermissionNeeded": 5},
		with_app_command=True,
		enabled=True
	)
	@app_commands.describe(member_or_role="The member or role you wish to delete admin from.")
	async def admins_delete(self, ctx: commands.Context, member_or_role: Union[discord.Role, discord.Member]):
		bot = self.bot
		userAdminLevel = await get_admin_level(bot, ctx.guild, ctx.author.id)

		role = discord.utils.get(ctx.guild.roles, id=member_or_role.id)
		adminLevelRequired = 5 if role else 7

		if not userAdminLevel >= adminLevelRequired:
			title = "Warning - Insufficient Permissions"
			description = f"The `delete` option of this command is limited to the admin level **{adminLevelRequired}**!" if role else f"The `member` option of this command is limited to the admin level **{adminLevelRequired}**"
			insufficientPermissions = discord.Embed(title=title, description=description, color=discord.Color.dark_gold())
			insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=insufficientPermissions)

		RESULTS = []

		dataset = await bot.admins.find_by_id(ctx.guild.id)

		if dataset:
			dataset['admins'][0]['name'] = ctx.guild.id
			RESULTS.append(dataset['admins'])

		if len(RESULTS) == 1:
			result_var = next((result for result in RESULTS if result[0]['name'] == RESULTS[0][0]['name']), None)

			if result_var is not None:
				result = result_var
				found = False
				for item in result:
					if item['MemberOrRole'] == member_or_role.id:
						result.remove(item)
						found = True

				if found:
					if len(dataset['admins']) == 0:
						await bot.admins.delete_by_id(dataset['_id'])
					else:
						await bot.admins.update_by_id(dataset)
					successEmbed = discord.Embed(title="Admin Level Removed", description=f"Successfully removed level admin {item['AdminLevel']} to {member_or_role.mention}", color=discord.Color.dark_blue())
					successEmbed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
					await ctx.send(embed=successEmbed)
				else:
					noAdmin = discord.Embed(title="Warning - Admin Level Not Found", description="This user or role does not have an assigned level admin, if you wish to change it, please add using `/admins add`.", color=discord.Color.dark_gold())
					noAdmin.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
					await ctx.send(embed=noAdmin)
			else:
				noAdmin = discord.Embed(title="Warning - Admin not found", description="The admin you are trying to delete was not found.", color=discord.Color.dark_gold())
				noAdmin.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
				await ctx.send(embed=noAdmin)

	@admins.command(
		name='view',
		description='Lists all the admin(s) in the server.',
		usage="/admins view",
		extras={"category": "Admins", "levelPermissionNeeded": 0},
		with_app_command=True,
		enabled=True
	)
	async def admins_view(self, ctx: commands.Context):
		bot = self.bot
		dataset = await bot.admins.find_by_id(ctx.guild.id)

		if not dataset:
			noAdmins = discord.Embed(title="Warning - No admins found", description="The server you are trying to view has no admins found.", color=discord.Color.dark_gold())
			noAdmins.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
			return await ctx.send(embed=noAdmins)

		result = sorted(dataset['admins'], key=lambda x: int(x['AdminLevel']))

		admin_levels = {}
		for item in result:
			if item['AdminLevel']:
				admin_levels.setdefault(item['AdminLevel'], []).append(item)

		serverAdmins = discord.Embed(
			title="Server Admins",
			description=f"Listing server level admins for the server {ctx.guild.name}",
			color=discord.Color.dark_blue()
		)
		serverAdmins.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

		for admin_level, actions in admin_levels.items():
			value = ""
			for action in actions:
				role = discord.utils.get(ctx.guild.roles, id=action['MemberOrRole'])
				value += f"- <@&{action['MemberOrRole']}>\n" if role else f"- <@{action['MemberOrRole']}>\n"
			serverAdmins.add_field(
				name=f"Admin Level {admin_level}",
				value=value,
				inline=True
			)

		await ctx.send(embed=serverAdmins)


async def setup(bot):
	await bot.add_cog(Admins(bot))
