from abc import *
from asyncmock import AsyncMock
from discord import Message


class Command(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def get_command_str(self) -> str:
        pass

    @abstractmethod
    async def execute(self, msg: Message, command_str: str, arguments: list):
        pass


def execute_condition_checker():
    def wrapper(func):
        def _wrapper(self, msg: Message, command_str: str, arguments: list):
            to_return = AsyncMock()
            to_return.x.return_value = True

            if self.get_command_str() != command_str:
                to_return.x.return_value = False
                return to_return.x()

            # 권한 체크

            return func(self, msg, command_str, arguments)
        return _wrapper
    return wrapper
