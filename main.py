import logging

from django.core.wsgi import get_wsgi_application
from nextcord import Game

from actions.action_dispatcher import *
from commands.command_dispatcher import *
from schedules.initial_schedules import *
from emoji_container import *
from helper_functions import *


def dispatch_action():
    def wrapper(func):
        async def _wrapper(self, *args, **kwargs):
            await func(self, *args, **kwargs)
            await execute_action(func.__qualname__.split('.')[1], *args, **kwargs,
                                 main_global=globals(), bot=self, commands_map=commands_map, actions=actions,
                                 alias_map=alias_map)
        return _wrapper
    return wrapper


class DiscordBot(nextcord.Client):
    def __init__(self):
        super().__init__(activity=Game(name="`help" if not IS_TESTING else "테스트"))

        self.emoji_cache_guilds = None

        def default_func(func_name):
            async def inner(this, *args, **kwargs):
                await execute_action(func_name, *args, **kwargs,
                                     main_global=globals(), bot=self, commands_map=commands_map, actions=actions,
                                     alias_map=alias_map)
            return inner

        for event in Action.EVENTS:
            attr_name = "on_" + event
            if not hasattr(self, attr_name):
                self.__setattr__("on_" + event, default_func(attr_name).__get__(self))

    @dispatch_action()
    async def on_ready(self):
        print("Ready!")
        self.emoji_cache_guilds = list(filter(lambda x: x.name == "yeshjho_emoji1님의 서버", self.guilds))

        if RESET_CACHE_EMOJIS:
            for guild in self.emoji_cache_guilds:
                for emoji in guild.emojis:
                    print("deleting an emoji")
                    await emoji.delete()

        emoji_container.initialize_cache(self.emoji_cache_guilds, self.emojis)

        schedule_initial(main_global=globals(), bot=self, commands_map=commands_map, actions=actions,
                         alias_map=alias_map)

    @dispatch_action()
    async def on_message(self, msg: nextcord.Message):
        if msg.author.bot:
            return

        if msg.content.startswith(COMMAND_PREFIX) and msg.content.count(COMMAND_PREFIX) == 1:
            split_content = msg.content.split(' ')
            await execute_command(msg, split_content[0][len(COMMAND_PREFIX):].lower(), split_content[1:],
                                  main_global=globals(), bot=self, commands_map=commands_map, actions=actions,
                                  alias_map=alias_map)
            return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', "settings")
    django_app = get_wsgi_application()

    discord_bot = DiscordBot()
    loop = asyncio.get_event_loop()
    discord_bot.loop.create_task(Scheduler.main_loop())
    try:
        loop.run_until_complete(discord_bot.start(os.getenv('DISCORD_BOT_KEY', 'err')))
    except KeyboardInterrupt:
        loop.run_until_complete(discord_bot.close())
    finally:
        loop.close()
