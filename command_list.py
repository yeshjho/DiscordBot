from discord import Message

from commands.command_add_class import *
from commands.command_convert_to_reactions import *

commands = [CommandAddClass(), CommandConvertToReactions()]


async def execute_command(msg: Message, command_str: str, arguments: list):
    for command in commands:
        if await command.execute(msg, command_str, arguments):
            return
