from commands.command import *

from constants import *


class CommandVersion(Command):
    """

    버전을 출력함
    봇의 버전을 출력합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "version"

    @execute_condition_checker()
    async def execute(self, msg: Message, arguments: list, *args, **kwargs):
        await msg.channel.send(VERSION)
