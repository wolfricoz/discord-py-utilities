import logging
import re

import discord
from discord.ext import commands

from .permissions import check_missing_channel_permissions, find_first_accessible_text_channel


def extract_invite_code(invite_url: str) -> str | None :
	"""Extracts the invite code from a Discord invite URL."""
	match = re.search(r"(?:https?://)?(?:www\.)?discord(?:\.gg|app\.com/invite)/([a-zA-Z0-9-]+)", invite_url)
	return match.group(1) if match else invite_url


async def check_guild_invites(bot: commands.AutoShardedBot, guild: discord.Guild, current_invite=None, channel: discord.TextChannel | discord.ForumChannel | discord.VoiceChannel = None, max_age=604800) -> str :
	invite: None | discord.Invite = None

	if current_invite and await check_invite(bot, guild, current_invite) :
		return current_invite
	try :
		reason = "Using config to create invite here"
		if not channel:
			channel = find_first_accessible_text_channel(guild)
			reason = f"Missing Invite/Invalid invite, making a new one."

		perms = check_missing_channel_permissions(channel, ["view_channel", "create_instant_invite"])
		if len(perms) < 1 :
			invite: str = await create_invite(channel, reason=reason, max_age=max_age)
		else:
			invite: str = "No permissions: " + ", ".join(perms)
		return invite
	except discord.Forbidden :
		logging.info(f"No permission to create invites in {guild.name}")
	try :
		invite: discord.Invite = (await guild.invites())[0]
		return invite.url
	except discord.Forbidden :
		logging.info(f"No permission to fetch invites in {guild.name}")
		return "forbidden"
	except IndexError :
		logging.info(f"{guild.name} has no invites.")
		return "no invites available"
	except Exception as e :
		logging.error(f"Error creating invite: {e}")
		return "error creating invite"


async def create_invite(channel: discord.TextChannel, reason=None, max_age=604800) -> str :
	try :
		invite = await channel.create_invite(max_age=604800, reason=reason)
		return invite.url
	except discord.Forbidden :
		return 'No permission'
	except Exception as e :
		logging.warning(f"Error creating invite: {e}")
		return f'No permission/Error'

async def check_invite(bot, guild: discord.Guild, invite: str) -> str | None :
	"""
	Checks if the invite is valid.

	:param bot:
	:param guild:
	:param invite:
	:return:
	"""
	# Check if the invite is in the list
	all_invites = await guild.invites()
	if any(invite == i.url or i == i.code for i in all_invites):
		return invite

	# If not, we try to fetch it; this feature can be unreliable at times.
	try :
		invite_code = extract_invite_code(invite)
		invite = await bot.fetch_invite(invite_code)
		return invite.url
	except (discord.HTTPException, discord.NotFound) :
		logging.info(f"{guild.name}'s invite expired or is invalid, creating a new one.")
	except ValueError :
		logging.info(f"{guild.name} has weird characters in invite code: {invite}")
