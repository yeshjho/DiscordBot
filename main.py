from discord import Game
import logging

from actions.action_dispatcher import *
from commands.command_dispatcher import *
from emoji_container import *
from helper_functions import *


logging.basicConfig(level=logging.INFO)


def dispatch_action():
    def wrapper(func):
        async def _wrapper(self, *args, **kwargs):
            await func(self, *args, **kwargs)
            await execute_action(func.__qualname__.split('.')[1], *args, **kwargs,
                                 main_global=globals(), bot=self, commands_map=commands_map, actions=actions,
                                 alias_map=alias_map)
        return _wrapper
    return wrapper


class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__(activity=Game(name="`help" if not IS_TESTING else "테스트"))

        self.emoji_cache_guilds = None

    async def on_ready(self):
        print("Ready!")

        self.emoji_cache_guilds = list(filter(lambda x: x.name == "yeshjho_emoji1님의 서버", self.guilds))
        emoji_container.initialize_cache(self.emoji_cache_guilds, self.emojis)

    @dispatch_action()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        if msg.content.startswith(COMMAND_PREFIX) and msg.content.count(COMMAND_PREFIX) == 1:
            split_content = msg.content.split(' ')
            await execute_command(msg, split_content[0][len(COMMAND_PREFIX):], split_content[1:],
                                  main_global=globals(), bot=self, commands_map=commands_map, actions=actions,
                                  alias_map=alias_map)
            return

    @dispatch_action()
    async def on_typing(self, channel, user, when):
        if user == self.user:
            return

    @dispatch_action()
    async def on_message_delete(self, msg):
        pass

    @dispatch_action()
    async def on_bulk_message_delete(self, msgs):
        pass

    @dispatch_action()
    async def on_message_edit(self, before, after):
        if after.author == self.user:
            return

    @dispatch_action()
    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return

    @dispatch_action()
    async def on_reaction_remove(self, reaction, user):
        if user == self.user:
            return

    @dispatch_action()
    async def on_reaction_clear(self, msg, reactions):
        pass

    @dispatch_action()
    async def on_reaction_clear_emoji(self, reaction):
        pass

    @dispatch_action()
    async def on_private_channel_create(self, channel):
        pass

    @dispatch_action()
    async def on_private_channel_delete(self, channel):
        pass

    @dispatch_action()
    async def on_private_channel_update(self, before, after):
        pass

    @dispatch_action()
    async def on_private_channel_pins_update(self, channel, last_pin):
        pass

    @dispatch_action()
    async def on_guild_channel_create(self, channel):
        pass

    @dispatch_action()
    async def on_guild_channel_delete(self, channel):
        pass

    @dispatch_action()
    async def on_guild_channel_update(self, before, after):
        pass

    @dispatch_action()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        pass

    @dispatch_action()
    async def on_guild_integrations_update(self, guild):
        pass

    @dispatch_action()
    async def on_webhooks_update(self, channel):
        pass

    @dispatch_action()
    async def on_member_join(self, member):
        pass

    @dispatch_action()
    async def on_member_remove(self, member):
        pass

    @dispatch_action()
    async def on_member_update(self, before, after):
        pass

    @dispatch_action()
    async def on_user_update(self, before, after):
        pass

    @dispatch_action()
    async def on_guild_join(self, guild):
        pass

    @dispatch_action()
    async def on_guild_remove(self, guild):
        pass

    @dispatch_action()
    async def on_guild_update(self, before, after):
        pass

    @dispatch_action()
    async def on_guild_role_create(self, role):
        pass

    @dispatch_action()
    async def on_guild_role_delete(self, role):
        pass

    @dispatch_action()
    async def on_guild_role_update(self, before, after):
        pass

    @dispatch_action()
    async def on_guild_emojis_update(self, guild, before, after):
        pass

    @dispatch_action()
    async def on_guild_available(self, guild):
        pass

    @dispatch_action()
    async def on_guild_unavailable(self, guild):
        pass

    @dispatch_action()
    async def on_voice_state_update(self, member, before, after):
        pass

    @dispatch_action()
    async def on_member_ban(self, guild, user):
        pass

    @dispatch_action()
    async def on_member_unban(self, guild, user):
        pass

    @dispatch_action()
    async def on_invite_create(self, invite):
        pass

    @dispatch_action()
    async def on_invite_delete(self, invite):
        pass

    @dispatch_action()
    async def on_group_join(self, channel, user):
        pass

    @dispatch_action()
    async def on_group_remove(self, channel, user):
        pass


if __name__ == "__main__":
    discord_bot = DiscordBot()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(discord_bot.start(BOT_KEY))
    except KeyboardInterrupt:
        loop.run_until_complete(discord_bot.logout())
    finally:
        loop.close()
