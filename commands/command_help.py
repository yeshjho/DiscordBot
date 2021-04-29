from commands.command import *

from constants import *
from helper_functions import *


class CommandHelp(Command):
    """
    [command]
    도움말을 보여줌
    도움말을 보여줍니다. command를 넣으면 해당 명령어에 대한 자세한 도움말을 보여줍니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "help"

    @staticmethod
    def get_syntax(command_str: str, doc: str):
        return COMMAND_PREFIX + command_str + ' ' + [line.lstrip() for line in doc.splitlines()][1]

    @staticmethod
    def get_short_explanation(doc: str):
        return [line.lstrip() for line in doc.splitlines()][2]

    @staticmethod
    def get_long_explanation(doc: str):
        return '\n'.join([line.lstrip() for line in doc.splitlines()][3:])

    @execute_condition_checker()
    async def execute(self, msg: Message, arguments: list, *args, **kwargs):
        commands_map = kwargs['commands_map']
        if len(arguments) >= 1:
            arg_command = arguments[0]
            target_command = commands_map[arg_command]
            doc = target_command.__doc__

            embed = get_embed(arg_command)
            embed.add_field(name=CommandHelp.get_syntax(arg_command, doc),
                            value=CommandHelp.get_long_explanation(doc))
            await msg.channel.send(embed=embed)
        else:
            embed = get_embed("설명서")
            for command_str, command_ in commands_map.items():
                doc = command_.__doc__

                embed.add_field(name=CommandHelp.get_syntax(command_str, doc),
                                value=CommandHelp.get_short_explanation(doc))
            await msg.channel.send(embed=embed)
