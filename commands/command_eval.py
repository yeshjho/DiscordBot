from commands.command import *

from traceback import format_exc

from helper_functions import *


class CommandEval(Command):
    """
    <code>
    파이썬 코드를 실행
    주어진 파이썬 코드를 봇의 최상단 글로벌 스코프 안에서 실행해 결과를 출력합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "eval"

    def get_command_permission_level(self) -> int:
        return EPermissionLevel.OWNER

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('code', nargs='*')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        try:
            result = eval(' '.join(args.code), kwargs['main_global'], locals())
        except BaseException:
            result = format_exc()

        await send_split(msg.channel, str(result), "```\n", "\n```")
