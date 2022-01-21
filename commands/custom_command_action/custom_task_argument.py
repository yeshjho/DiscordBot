from abc import ABCMeta, abstractmethod
from enum import IntEnum, auto

from nextcord import TextChannel


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
    async def get_input(self, channel: TextChannel) -> str:
        pass

    # takes the argument stored in the db and reinterprets to its type
    @abstractmethod
    def parse(self, arg: str):
        pass


# TODO: 입력 받을 때 공통으로 이름 출력하고 ~~에 대한 입력을 받습니다 같은 거 할 거 같은데 얘네 처리?
class CustomTaskArgumentChannel(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.CHANNEL

    # special case
    async def get_input(self, channel: TextChannel) -> str:
        return 'channel'

    # special case, arg won't be a str but a channel object itself
    def parse(self, arg: str):
        return arg


class CustomTaskArgumentText(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.TEXT

    async def get_input(self, channel: TextChannel) -> str:
        # TODO
        pass

    def parse(self, arg: str):
        return arg
