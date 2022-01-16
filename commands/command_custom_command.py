from commands.command import *

from custom_command import guild_custom_commands, add_custom_command


class CommandCustomCommand(Command):
    """
    [create|edit|delete]
    서버 명령어 조회/관리
    이 서버만의 명령어를 조회/생성/수정/삭제합니다. 인자가 없으면 조회합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "command"

    def get_command_alias(self) -> list:
        return ["com", 'servercommand', '명령어', '서버명령어']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('mode', choices=['create', 'c', '생성', '만들기', 'edit', 'e', '수정',
                                             'delete', 'remove', 'd', 'r', '삭제'])

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        from db_models.custom_command_action.models import CustomCommand

        if args.mode:
            return

        if args.mode == 'create' or args.mode == 'c' or args.mode == '생성' or args.mode == '만들기':
            return

        if args.mode == 'edit' or args.mode == 'e' or args.mode == '수정':
            return

        if args.mode == 'delete' or args.mode == 'remove' or args.mode == 'd' or args.mode == 'r' or args.mode == '삭제':
            return
