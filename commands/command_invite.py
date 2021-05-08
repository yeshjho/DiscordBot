from commands.command import *


class CommandInvite(Command):
    """

    초대 링크 출력
    이 봇을 초대할 수 있는 링크를 출력합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "invite"

    def get_command_alias(self) -> list:
        return ["inv", "초대"]

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        await msg.channel.send(INVITE_LINK)
