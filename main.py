import discord
from discord import Game
import asyncio

from commands.command_list import *
from constants import *
from helper_functions import *


class BuildBot(discord.Client):
    def __init__(self):
        super().__init__(activity=Game(name="`help"))

    @staticmethod
    async def on_ready():
        print("Ready!")

    async def on_message(self, msg: discord.Message):
        if msg.author == self.user:
            return

        if msg.content.startswith(COMMAND_PREFIX):
            split_content = msg.content.split(' ')
            await execute_command(msg, split_content[0][len(COMMAND_PREFIX):], split_content[1:], main_global=globals())


if __name__ == "__main__":

    build_bot = BuildBot()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(build_bot.start(BOT_KEY))
    except KeyboardInterrupt:
        loop.run_until_complete(build_bot.logout())
    finally:
        loop.close()
