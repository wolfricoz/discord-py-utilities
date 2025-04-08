import discord


async def check_missing_permissions(channel: discord.TextChannel, required_permissions: list) -> list :
	"""
	Check which permissions are missing for the bot in the specified channel.

	:param channel: The channel to check permissions for.
	:param required_permissions: A list of required permissions to check.
	:return: A list of missing permissions.
	"""
	bot_permissions = channel.permissions_for(channel.guild.me)
	missing_permissions = [perm for perm in required_permissions if not getattr(bot_permissions, perm)]
	return missing_permissions
