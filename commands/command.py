from abc import ABCMeta, abstractmethod
import argparse
from asyncmock import AsyncMock

from discord import Message

from common import ECommandExecuteResult
from permissions import *


class CommandExecuteError(Exception):
    pass


class Command(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def get_command_str(self) -> str:
        pass

    def get_command_alias(self) -> list:
        return []

    def get_command_permission_level(self) -> int:
        return EPermissionLevel.ALL

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        pass

    @abstractmethod
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        pass

    async def on_custom_error(self, msg: Message, arguments: list):
        await msg.channel.send(' '.join(arguments))


def execute_condition_checker():
    def wrapper(func):
        async def _wrapper(self, msg: Message, arguments: list, *args, **kwargs):
            to_return = AsyncMock()

            if self.get_command_permission_level() > permissions.get_permission_level(msg.author):
                to_return.x.return_value = ECommandExecuteResult.NO_PERMISSION
                return await to_return.x()

            to_return.x.return_value = await func(self, msg, arguments, *args, **kwargs)
            if to_return.x.return_value is None:
                to_return.x.return_value = ECommandExecuteResult.SUCCESS

            return await to_return.x()
        return _wrapper
    return wrapper
