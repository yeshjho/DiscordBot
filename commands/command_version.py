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

    def get_command_alias(self) -> list:
        return ["v", "ver", "버전"]

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        await msg.channel.send(VERSION)
