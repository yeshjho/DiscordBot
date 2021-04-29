from commands.command import *


class CommandAddClass(Command):
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "add_class"

    @execute_condition_checker()
    async def execute(self, msg: Message, command_str: str, arguments: list):
        pass
