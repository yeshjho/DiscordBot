import argparse
from importlib import import_module
from glob import glob

from discord import Message

from commands.command import ECommandExecuteResult
from helper_functions import *

commands = []

EXCLUDES = ['command_dispatcher']
for command_file in glob('commands/**/*.py', recursive=True):
    module_name = ''.join(command_file.split('.')[:-1]).replace('\\', '.').replace('/', '.')
    file_name = module_name.split('.')[-1]
    if file_name.startswith('command_') and file_name not in EXCLUDES:
        module = import_module(module_name)
        class_name = ''.join([c[0].upper() + c[1:] for c in file_name.split('_')])
        commands.append(module.__dict__[class_name]())

commands_map = dict([(command.get_command_str(), command) for command in commands])
alias_map = {}
for command in commands:
    for alias in command.get_command_alias():
        alias_map[alias] = command.get_command_str()


class NonExitingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise argparse.ArgumentError(None, "")


async def execute_command(msg: Message, command_str: str, args: list, **kwargs):
    if IS_TESTING and msg.author.id != OWNER_ID:
        return

    command_str = alias_map.get(command_str, command_str)
    if command_str in commands_map:
        command = commands_map[command_str]

        parser = NonExitingArgumentParser(add_help=False)
        command.fill_arg_parser(parser)
        try:
            args_namespace, _ = parser.parse_known_args(args)
        except argparse.ArgumentError:
            return_value = ECommandExecuteResult.SYNTAX_ERROR
        else:
            return_value = await command.execute(msg, args_namespace, **kwargs)

        additional_args = []
        if type(return_value) is tuple:
            additional_args = return_value[1:]
            return_value = return_value[0]

        if return_value == ECommandExecuteResult.SUCCESS:
            return

        elif return_value == ECommandExecuteResult.NO_PERMISSION:
            await msg.channel.send(mention_user(msg.author) + " 이 명령어를 실행할 권한이 없습니다!")

        elif return_value == ECommandExecuteResult.SYNTAX_ERROR:
            fake_namespace = argparse.Namespace()
            fake_namespace.__setattr__('command', command_str)
            await commands_map['help'].execute(msg, fake_namespace, **kwargs)

        elif return_value == ECommandExecuteResult.CUSTOM_ERROR:
            await command.on_custom_error(msg, additional_args)

        else:
            raise

    else:
        await msg.channel.send(mention_user(msg.author) + " 모르는 명령어입니다. 도움말을 보려면 `help를 입력하세요.")
