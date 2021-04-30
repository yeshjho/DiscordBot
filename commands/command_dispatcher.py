from importlib import import_module
from glob import glob

from discord import Message

from commands.command import ECommandExecuteResult
from constants import *
from helper_functions import *

commands = []

EXCLUDES = ['command_dispatcher.py']
for command_file in glob('commands/*.py'):
    command_file = command_file.split('\\')[1] if '\\' in command_file else command_file.split('/')[1]
    if command_file.startswith('command_') and command_file not in EXCLUDES:
        file_name = command_file.split('.')[0]
        module = import_module('commands.' + file_name)
        class_name = ''.join([c[0].upper() + c[1:] for c in file_name.split('_')])
        commands.append(module.__dict__[class_name]())

commands_map = dict([(command.get_command_str(), command) for command in commands])


async def execute_command(msg: Message, command_str: str, arguments: list, *args, **kwargs):
    if IS_TESTING and msg.author.id != OWNER_ID:
        return

    if command_str in commands_map:
        return_value = await commands_map[command_str].execute(msg, arguments, *args, **kwargs,
                                                               commands_map=commands_map)
        additional_args = []
        if type(return_value) is tuple:
            additional_args = return_value[1:]
            return_value = return_value[0]

        if return_value == ECommandExecuteResult.SUCCESS:
            return
        elif return_value == ECommandExecuteResult.NO_PERMISSION:
            await msg.channel.send(mention_user(msg.author) + " 이 명령어를 실행할 권한이 없습니다!")
        elif return_value == ECommandExecuteResult.SYNTAX_ERROR:
            await commands_map['help'].execute(msg, [command_str], *args, **kwargs, commands_map=commands_map)
        elif return_value == ECommandExecuteResult.CUSTOM_ERROR:
            await commands_map[command_str].on_custom_error(msg, additional_args)
        else:
            raise

    else:
        await msg.channel.send(mention_user(msg.author) + " 모르는 명령어입니다. 도움말을 보려면 `help를 입력하세요.")