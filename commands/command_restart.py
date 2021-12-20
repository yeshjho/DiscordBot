from commands.command import *

import sys


class CommandRestart(Command):
    """

    봇 재시작
    봇을 재시작합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "restart"

    def get_command_alias(self) -> list:
        return ["reboot", "재시작", "리붓", "리부팅"]

    def get_command_permission_level(self) -> int:
        return EPermissionLevel.ADMIN

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        await msg.channel.send("restarting...")
        sys.exit(1)  # service is configured to restart on error
