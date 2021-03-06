from commands.command import *

from helper_functions import *
from .custom_command_action.custom_task import custom_tasks


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

    def get_command_alias(self) -> list:
        return ["h", "도움", "도움말", "명령어"]

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('command', nargs='?', default=None)

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
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        commands_map = kwargs['commands_map']
        if args.command:
            guild_custom_commands = kwargs['guild_custom_commands']
            custom_commands = guild_custom_commands.get(msg.guild.id if msg.guild else 0, {})
            if args.command in custom_commands:
                target_command = custom_commands[args.command]

                embed = get_embed(args.command, '이 서버의 커스텀 명령어')
                obj = target_command.model_object
                task = custom_tasks[obj.task]
                embed.add_field(name=args.command, value=task.get_format_string(*obj.get_args()), inline=False)
                embed.set_image(url=FORCE_FULL_WIDTH_IMAGE_URL)
                await msg.channel.send(embed=embed)

                return

            target_command = commands_map.get(args.command, None)
            if not target_command:
                target_command = commands_map.get(kwargs['alias_map'].get(args.command, None), None)

            if not target_command:
                raise CommandExecuteError("존재하지 않는 명령어입니다!", delete_after=1)

            doc = target_command.__doc__

            target_command_str = target_command.get_command_str()

            embed = get_embed(target_command_str)
            embed.add_field(name=CommandHelp.get_syntax(target_command_str, doc),
                            value=CommandHelp.get_long_explanation(doc))

            aliases = dict(filter(lambda x: x[1] == target_command_str, kwargs['alias_map'].items()))
            if aliases:
                embed.set_footer(text="다른 이름: " + ", ".join(aliases.keys()))
            await msg.channel.send(embed=embed)

        else:
            embed = get_embed("도움말")
            for command_str, command_ in sorted(commands_map.items()):
                doc = command_.__doc__

                embed.add_field(name=CommandHelp.get_syntax(command_str, doc),
                                value=CommandHelp.get_short_explanation(doc))
            await msg.channel.send(embed=embed)
