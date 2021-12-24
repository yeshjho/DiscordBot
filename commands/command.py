from abc import ABCMeta, abstractmethod
import argparse
from asyncmock import AsyncMock

from nextcord import Message

from common import ECommandExecuteResult, EPermissionLevel
from helper_functions import mention_user


class CommandExecuteError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.kwargs = kwargs


class Command(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def get_command_str(self) -> str:
        pass

    def get_command_alias(self) -> list:
        return []

    def get_command_permission_level(self) -> int:
        return EPermissionLevel.DEFAULT

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        pass

    @abstractmethod
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        pass

    async def on_custom_error(self, msg: Message, *args, **kwargs):
        await msg.channel.send(mention_user(msg.author) + ' '.join(args), delete_after=kwargs.get('delete_after', None))


def execute_condition_checker():
    def wrapper(func):
        async def _wrapper(self, msg: Message, args: argparse.Namespace, **kwargs):
            to_return = AsyncMock()

            if self.get_command_permission_level() > args.permission_level:
                to_return.x.return_value = ECommandExecuteResult.NO_PERMISSION
                return await to_return.x()

            to_return.x.return_value = await func(self, msg, args, **kwargs)
            if to_return.x.return_value is None:
                to_return.x.return_value = ECommandExecuteResult.SUCCESS

            return await to_return.x()
        return _wrapper
    return wrapper
