import discord
from discord.ext import commands


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

	@discord.ui.button(style=discord.ButtonStyle.secondary, label="Previous Page", disabled=True)
	async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		if interaction.user.id != self.user_id:
			invalidAction=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This button does not belong to you',
				color = 0xc27d0e,
			)
			invalidAction.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.followup.send(embed=invalidAction, ephemeral=True)
		await self.paginate(interaction.message, -1)

	@discord.ui.button(style=discord.ButtonStyle.secondary, label="Next Page", disabled=False)
	async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		if interaction.user.id != self.user_id:
			invalidAction=discord.Embed(
				title = 'Warning - Invalid Action',
				description= 'This button does not belong to you',
				color = 0xc27d0e,
			)
			invalidAction.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.followup.send(embed=invalidAction, ephemeral=True)
		await self.paginate(interaction.message, 1)

		