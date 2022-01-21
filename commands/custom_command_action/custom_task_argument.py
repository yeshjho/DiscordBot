from abc import ABCMeta, abstractmethod
from enum import IntEnum, auto

from nextcord import TextChannel, Client, User

from helper_functions import *


class ECustomTaskArgumentType(IntEnum):
    CHANNEL = auto()
    TEXT = auto()
    USER_MENTION = auto()


class CustomTaskArgument(metaclass=ABCMeta):
    def __init__(self, arg_name: str):
        self.arg_name: str = arg_name

    @property
    @abstractmethod
    def type(self) -> ECustomTaskArgumentType:
        pass

    # gets an input from user and returns a string storeable in the db
    @abstractmethod
    async def get_input(self, bot: Client, user: User, channel: TextChannel) -> str:
        pass

    # takes the argument stored in the db and reinterprets to its type
    @abstractmethod
    def parse(self, arg: str):
        pass

    @property
    def no_prompt(self) -> bool:
        return False


class CustomTaskArgumentChannel(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.CHANNEL

    # special case
    async def get_input(self, bot: Client, user: User, channel: TextChannel) -> str:
        return 'channel'

    # special case, arg won't be a str but a channel object itself
    def parse(self, arg: str):
        return arg

    @property
    def no_prompt(self) -> bool:
        return True


class CustomTaskArgumentText(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.TEXT

    async def get_input(self, bot: Client, user: User, channel: TextChannel) -> str:
        return (await bot.wait_for('message', check=lambda x: x.author.id == user.id, timeout=60)).content

    def parse(self, arg: str):
        return arg


class CustomTaskArgumentUserMention(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.USER_MENTION

    async def get_input(self, bot: Client, user: User, channel: TextChannel) -> str:
        return (await bot.wait_for('message', check=lambda x: x.author.id == user.id and
                                                              x.content.startswith("<@") and x.content.endswith('>'),
                                   timeout=60)).content

    def parse(self, arg: str):
        return arg
