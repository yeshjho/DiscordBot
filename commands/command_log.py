from commands.command import *

import datetime

from helper_functions import *


class CommandLog(Command):
    """
    <date>
    로그 조회
    해당 날짜의 로그를 조회합니다. date의 형식은 YYYY-MM-DD입니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "log"

    def get_command_alias(self) -> list:
        return ["로그"]

    def get_command_permission_level(self) -> int:
        return 1001

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('date')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        try:
            datetime.datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            return ECommandExecuteResult.SYNTAX_ERROR

        try:
            with open('logs/' + args.date + '.txt', encoding='utf-8') as log_file:
                await send_split(msg.channel, log_file.read(), '```\n', '\n```')
        except FileNotFoundError:
            raise CommandExecuteError(mention_user(msg.author), "해당 날짜는 로그가 없어요!", delete_after=2)
