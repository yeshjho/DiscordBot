import argparse
from django.core.exceptions import ObjectDoesNotExist
from importlib import import_module
from glob import glob

from nextcord import Message

from commands.command import CommandExecuteError
from helper_functions import *
from logger import *

commands = []

EXCLUDES = ['command_dispatcher', 'command_word']
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
    import db_models.common.models as models

    if IS_TESTING and msg.author.id != OWNER_ID:
        await msg.channel.send(mention_user(msg.author) + " 테스트 중엔 사용할 수 없어요!", delete_after=1)
        return

    command_str = alias_map.get(command_str, command_str)
    if command_str not in commands_map:
        await msg.channel.send(mention_user(msg.author) + " 모르는 명령어입니다. 도움말을 보려면 `help를 입력하세요.")
        return

    user, _ = models.User.objects.get_or_create(id=msg.author.id)
    permission_levels = [models.UserPermission.objects.get_or_create(user=user)[0].level]
    kwargs["user"] = user

    if msg.guild:
        guild, _ = models.Guild.objects.get_or_create(id=msg.guild.id)
        try:
            permission_levels.append(models.GuildPermission.objects.get(guild__id=guild.id).level)
        except ObjectDoesNotExist:
            pass
        kwargs['guild'] = guild

        roles = []
        for role in msg.author.roles:
            role_, _ = models.Role.objects.get_or_create(id=role.id, guild=guild)
            roles.append(role_)
            try:
                permission_levels.append(models.RolePermission.objects.get(role__id=role.id).level)
            except ObjectDoesNotExist:
                pass
        kwargs['roles'] = roles

    kwargs['permission_level'] = max(permission_levels)

    Logger.log("Executing command:", command_str, "with", msg.content)

    command = commands_map[command_str]

    parser = NonExitingArgumentParser(add_help=False)
    command.fill_arg_parser(parser)

    additional_args = []
    additional_kwargs = {}
    try:
        args_namespace, _ = parser.parse_known_args(args)
    except argparse.ArgumentError:
        return_value = ECommandExecuteResult.SYNTAX_ERROR
    else:
        try:
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
        await commands_map['help'].execute(msg, fake_namespace, **kwargs)

    elif return_value == ECommandExecuteResult.CUSTOM_ERROR:
        await command.on_custom_error(msg, *additional_args, **additional_kwargs)

    else:
        raise

    log_command(command_str, msg, return_value, additional_args)
