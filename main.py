import logging

from django.core.wsgi import get_wsgi_application
from nextcord import Game

from actions.action_dispatcher import Action, execute_action, actions
from commands.custom_command_action.custom_command import CustomCommand, guild_custom_commands
from commands.command_dispatcher import commands_map, alias_map, execute_command
from schedules.initial_schedules import schedule_initial, Scheduler
from emoji_container import *
from helper_functions import *


common_kwargs = {
    'commands_map': commands_map,
    'actions': actions,
    'alias_map': alias_map,
    'guild_custom_commands': guild_custom_commands
}


def dispatch_action():
    def wrapper(func):
        async def _wrapper(self, *args, **kwargs):
            await func(self, *args, **kwargs)
            await execute_action(func.__qualname__.split('.')[1], *args, **kwargs,
                                 main_global=globals(), bot=self, **common_kwargs)
        return _wrapper
    return wrapper


class DiscordBot(nextcord.Client):
    def __init__(self, **kwargs):
        super().__init__(activity=Game(name="`help" if not IS_TESTING else "테스트"), **kwargs)

        self.emoji_cache_guilds = None

        def default_func(func_name):
            async def inner(this, *args, **kwargs):
                await execute_action(func_name, *args, **kwargs,
                                     main_global=globals(), bot=self, **common_kwargs)
            return inner

        for event in Action.EVENTS:
            attr_name = "on_" + event
            if not hasattr(self, attr_name):
                self.__setattr__("on_" + event, default_func(attr_name).__get__(self))

    @dispatch_action()
    async def on_ready(self):
        self.emoji_cache_guilds = list(filter(lambda x: x.name == "yeshjho_emoji1님의 서버", self.guilds))

        if RESET_CACHE_EMOJIS:
            for guild in self.emoji_cache_guilds:
                for emoji in guild.emojis:
                    print("deleting an emoji")
                    await emoji.delete()

        emoji_container.initialize_cache(self.emoji_cache_guilds, self.emojis)

        await self.fetch_guilds().flatten()

        schedule_initial(main_global=globals(), bot=self, **common_kwargs)
        CustomCommand.load()

        print("Ready!")

    @dispatch_action()
    async def on_message(self, msg: nextcord.Message):
        if msg.author.bot:
            return

        if msg.content.startswith(COMMAND_PREFIX) and msg.content.count(COMMAND_PREFIX) == 1:
            split_content = msg.content.split(' ')
            await execute_command(msg, split_content[0][len(COMMAND_PREFIX):].lower(), split_content[1:],
                                  main_global=globals(), bot=self, **common_kwargs)
            return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    django_app = get_wsgi_application()

    intents = nextcord.Intents.all()
    discord_bot = DiscordBot(intents=intents)
    loop = asyncio.get_event_loop()
    discord_bot.loop.create_task(Scheduler.main_loop())
    try:
        loop.run_until_complete(discord_bot.start(os.getenv('DISCORD_BOT_KEY', 'err')))
    except KeyboardInterrupt:
        loop.run_until_complete(discord_bot.close())
    finally:
        loop.close()
