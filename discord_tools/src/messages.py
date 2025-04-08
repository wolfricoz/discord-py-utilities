import logging

import discord
from discord.ext.commands.help import MISSING

from discord_tools.src.exceptions import NoChannelException, NoMessagePermissionException
from discord_tools.src.permissions import check_missing_permissions

MAX_LENGTH = 1800


async def send_message(channel: discord.TextChannel | discord.User | discord.Member, message: str = None, embed=None,
                       view=None, files=None,
                       ) -> discord.Message :
	"""Send a message to a channel, if there is no permission it will send an error message to the owner. Automatically handles messages longer than 2000 characters by splitting them into multiple messages."""
	last_message = None
	if channel is None :
		raise NoChannelException
	try :
		length = 0
		if message is None :
			return await channel.send(embed=embed, view=view, files=files)
		while length < len(message) :
			last_message = await channel.send(message[length :length + MAX_LENGTH], embed=embed, view=view, files=files)
			length += MAX_LENGTH
		else :
			return last_message
	except discord.errors.Forbidden :
		required_perms = ['view_channel', 'send_messages', 'embed_links', 'attach_files']
		missing_perms = await check_missing_permissions(channel, required_perms)
		logging.error(f"Missing permission to send message to {channel.mention} in {channel.guild.name}")
		await channel.guild.owner.send(
			f"Missing permission to send message to {channel.name}. Check permissions: {', '.join(missing_perms)}", )
		raise NoMessagePermissionException(missing_permissions=missing_perms)


async def send_response(interaction: discord.Interaction, response, ephemeral=False, view=MISSING, embed=MISSING) :
	"""Sends a response to an interaction. If the interaction is already responded, it will send a followup message."""
	try :

		return await interaction.response.send_message(response, ephemeral=ephemeral, view=view, embed=embed, )
	except discord.errors.Forbidden :
		required_perms = ['view_channel', 'send_messages', 'embed_links', 'attach_files']
		missing_perms = await check_missing_permissions(interaction.channel, required_perms)
		logging.error(f"Missing permission to send message to {interaction.channel.name}")
		await interaction.guild.owner.send(
			f"Missing permission to send message to {interaction.channel.name}. Check permissions: {', '.join(missing_perms)}", )
		raise NoMessagePermissionException(missing_permissions=missing_perms)
	except discord.errors.NotFound or discord.InteractionResponded :
		try :
			await interaction.followup.send(
				response,
				ephemeral=ephemeral,
				view=view,
				embed=embed,

			)
		except discord.errors.NotFound :
			await send_message(interaction.channel, response, view=view, embed=embed)
	except Exception :
		return await interaction.channel.send(response, view=view, embed=embed)


async def await_message(interaction, message) -> discord.Message | bool :
	"""Wait for a message from the user that triggered the interaction. If the message is 'cancel', return False."""
	msg: discord.Message = await send_message(interaction.channel,
	                                          message)

	def check_message(m, interaction) :
		return m.author == interaction.user and m.channel == interaction.channel

	m = await interaction.client.wait_for('message', check=lambda m : check_message(m, interaction), timeout=600)
	await msg.delete()
	if m.content.lower() == "cancel" :
		return False
	return m