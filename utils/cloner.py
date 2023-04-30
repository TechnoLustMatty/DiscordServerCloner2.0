import discord
from colorama import Fore, init, Style
import asyncio
import sys, json

with open("./utils/config.json", "r") as json_file:
  data = json.load(json_file)
  logs_enabled = data["logs"]


def clear_line(n=1):
  LINE_UP = '\033[1A'
  LINE_CLEAR = '\x1b[2K'
  for _ in range(n):
    print(LINE_UP, end=LINE_CLEAR)


def logs(message, type, number=None):
  if logs_enabled:
    log_types = {
      'add': ('[+]', Fore.GREEN),
      'delete': ('[-]', Fore.RED),
      'warning': ('[WARNING]', Fore.YELLOW),
      'error': ('[ERROR]', Fore.RED)
    }
    prefix, color = log_types.get(type, ('[?]', Fore.RESET))

    if number is not None:
      print(f" {color}{prefix}{Style.RESET_ALL} {message}")
    else:
      print(f" {color}{prefix}{Style.RESET_ALL} {message}")
      clear_line()


class Cloner:

  @staticmethod
  async def guild_create(guild_to: discord.Guild, guild_from: discord.Guild):
    try:
      try:
        icon_image = await guild_from.icon_url_as(format='jpg').read()
      except discord.errors.DiscordException:
        logs(f"Can't read icon image from {guild_from.name}", 'error')
        icon_image = None
      await guild_to.edit(name=f'{guild_from.name}')
      if icon_image is not None:
        try:
          await guild_to.edit(icon=icon_image)
          logs(f"Guild Icon Changed: {guild_to.name}", 'add')
        except Exception:
          logs(f"Error While Changing Guild Icon: {guild_to.name}", 'error')
    except discord.errors.Forbidden:
      logs(f"Error While Changing Guild Icon: {guild_to.name}", 'error')
    logs(f"Cloned server: {guild_to.name}", 'add', True)

  @staticmethod
  async def roles_create(guild_to: discord.Guild, guild_from: discord.Guild):
    roles = [role for role in guild_from.roles if role.name != "@everyone"]
    roles.reverse()
    roles_created = len(roles)
    for role in roles:
      try:
        kwargs = {
          'name': role.name,
          'permissions': role.permissions,
          'colour': role.colour,
          'hoist': role.hoist,
          'mentionable': role.mentionable
        }
        await guild_to.create_role(**kwargs)
        logs(f"Created Role {role.name}", 'add')
      except (discord.Forbidden, discord.HTTPException) as e:
        logs(f"Error creating role {role.name}: {e}", 'error')
    logs(f"Created Roles: {roles_created}", 'add', True)

  @staticmethod
  async def channels_delete(guild_to: discord.Guild):
    channels = guild_to.channels
    channels_deleted = len(channels)
    for channel in channels:
      try:
        await channel.delete()
        logs(f"Deleted Channel: {channel.name}", 'delete')
      except (discord.Forbidden, discord.HTTPException) as e:
        logs(f"Error deleting channel {channel.name}: {e}", 'error')
    logs(f"Deleted Channels: {channels_deleted}", 'delete', True)

  @staticmethod
    async def categories_create(guild_to: discord.Guild, guild_from: discord.Guild):
        channels = guild_from.categories
        channel: discord.CategoryChannel
        new_channel: discord.CategoryChannel
        for channel in channels:
            try:
                overwrites_to = {}
                for key, value in channel.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    overwrites_to[role] = value
                new_channel = await guild_to.create_category(
                    name=channel.name,
                    overwrites=overwrites_to)
                await new_channel.edit(position=channel.position)
                print_add(f"Created Category: {channel.name}")
            except discord.Forbidden:
                print_error(f"Error While Deleting Category: {channel.name}")
            except discord.HTTPException:
                print_error(f"Unable To Delete Category: {channel.name}")

     @staticmethod
    async def channels_create(guild_to: discord.Guild, guild_from: discord.Guild):
        channel_text: discord.TextChannel
        channel_voice: discord.VoiceChannel
        category = None
        for channel_text in guild_from.text_channels:
            try:
                for category in guild_to.categories:
                    try:
                        if category.name == channel_text.category.name:
                            break
                    except AttributeError:
                        print_warning(f"Channel {channel_text.name} doesn't have any category!")
                        category = None
                        break

                overwrites_to = {}
                for key, value in channel_text.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    overwrites_to[role] = value
                try:
                    new_channel = await guild_to.create_text_channel(
                        name=channel_text.name,
                        overwrites=overwrites_to,
                        position=channel_text.position,
                        topic=channel_text.topic,
                        slowmode_delay=channel_text.slowmode_delay,
                        nsfw=channel_text.nsfw)
                except:
                    new_channel = await guild_to.create_text_channel(
                        name=channel_text.name,
                        overwrites=overwrites_to,
                        position=channel_text.position)
                if category is not None:
                    await new_channel.edit(category=category)
                print_add(f"Created Text Channel: {channel_text.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Text Channel: {channel_text.name}")
            except discord.HTTPException:
                print_error(f"Unable To Creating Text Channel: {channel_text.name}")
            except:
                print_error(f"Error While Creating Text Channel: {channel_text.name}")

        category = None
        for channel_voice in guild_from.voice_channels:
            try:
                for category in guild_to.categories:
                    try:
                        if category.name == channel_voice.category.name:
                            break
                    except AttributeError:
                        print_warning(f"Channel {channel_voice.name} doesn't have any category!")
                        category = None
                        break

                overwrites_to = {}
                for key, value in channel_voice.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    overwrites_to[role] = value
                try:
                    new_channel = await guild_to.create_voice_channel(
                        name=channel_voice.name,
                        overwrites=overwrites_to,
                        position=channel_voice.position,
                        bitrate=channel_voice.bitrate,
                        user_limit=channel_voice.user_limit,
                        )
                except:
                    new_channel = await guild_to.create_voice_channel(
                        name=channel_voice.name,
                        overwrites=overwrites_to,
                        position=channel_voice.position)
                if category is not None:
                    await new_channel.edit(category=category)
                print_add(f"Created Voice Channel: {channel_voice.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Voice Channel: {channel_voice.name}")
            except discord.HTTPException:
                print_error(f"Unable To Creating Voice Channel: {channel_voice.name}")
            except:
                print_error(f"Error While Creating Voice Channel: {channel_voice.name}")

  @staticmethod
  async def emojis_create(guild_to: discord.Guild, guild_from: discord.Guild):
    emoji: discord.Emoji
    emojis_created = len(guild_from.emojis)
    for emoji in guild_from.emojis:
      try:
        await asyncio.sleep(0.2)
        emoji_image = await emoji.url.read()
        await guild_to.create_custom_emoji(name=emoji.name, image=emoji_image)
        logs(f"Created Emoji {emoji.name}", 'add')
      except discord.Forbidden:
        logs(f"Error While Creating Emoji {emoji.name} ", 'error')
      except discord.HTTPException:
        logs(f"Error While Creating Emoji {emoji.name}", 'error')
    logs(f"Created Emojis: {emojis_created}", 'add', True)
