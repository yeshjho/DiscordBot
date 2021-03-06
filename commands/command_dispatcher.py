import argparse
from importlib import import_module
from glob import glob

from nextcord import Message

from commands.command import CommandExecuteError
from commands.custom_command_action.custom_command import guild_custom_commands
from helper_functions import *
from logger import *

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
        await msg.channel.send(mention_user(msg.author) + " 테스트 중엔 사용할 수 없어요!", delete_after=1)
        return

    custom_commands = guild_custom_commands.get(msg.guild.id if msg.guild else 0, {})
    if command_str in custom_commands:
        command = custom_commands[command_str]
    else:
        command_str = alias_map.get(command_str, command_str)
        if command_str not in commands_map:
            await msg.channel.send(mention_user(msg.author) + " 모르는 명령어입니다. 도움말을 보려면 `help를 입력하세요.")
            return
        command = commands_map[command_str]

    Logger.log("Executing " + ("custom " if command_str in custom_commands else "") + "command:",
               command_str, "with", msg.content)

    parser = NonExitingArgumentParser(add_help=False)
    command.fill_arg_parser(parser)

    additional_args = []
    additional_kwargs = {}
    permission_level = get_permission_level(msg.author.id, msg.guild.id, [role.id for role in msg.author.roles])
    try:
        args_namespace, extra_args = parser.parse_known_args(args)
        args_namespace.extra_args = extra_args
    except argparse.ArgumentError:
        return_value = ECommandExecuteResult.SYNTAX_ERROR
    else:
        try:
            args_namespace.permission_level = permission_level
            return_value = await command.execute(msg, args_namespace, **kwargs)
        except CommandExecuteError as err:
            return_value = ECommandExecuteResult.CUSTOM_ERROR
            additional_args = err.args
            additional_kwargs = err.kwargs

    if type(return_value) is tuple:
        additional_args = return_value[1:]
        return_value = return_value[0]

    if return_value == ECommandExecuteResult.SUCCESS:
        pass

    elif return_value == ECommandExecuteResult.NO_PERMISSION:
        await msg.channel.send(mention_user(msg.author) + " 이 명령어를 실행할 권한이 없습니다!")

    elif return_value == ECommandExecuteResult.SYNTAX_ERROR:
        fake_namespace = argparse.Namespace()
        fake_namespace.__setattr__('command', command_str)
        fake_namespace.permission_level = permission_level
        await commands_map['help'].execute(msg, fake_namespace, **kwargs)

    elif return_value == ECommandExecuteResult.CUSTOM_ERROR:
        await command.on_custom_error(msg, *additional_args, **additional_kwargs)

    else:
        raise

    log_command(command_str, msg, return_value, additional_args)
