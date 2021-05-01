from commands.command import *


class CommandKill(Command):
    """

    봇 종료
    봇을 종료합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "kill"

    def get_command_permission_level(self) -> int:
        return EPermissionLevel.ADMIN

    @execute_condition_checker()
    async def execute(self, msg: Message, arguments: list, *args, **kwargs):
        await kwargs['bot'].logout()
