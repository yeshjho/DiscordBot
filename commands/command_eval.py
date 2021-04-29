from commands.command import *

from traceback import format_exc

from constants import *


class CommandEval(Command):
    """
    [code]
    파이썬 코드를 실행
    주어진 파이썬 코드를 봇의 최상단 글로벌 스코프 안에서 실행해 결과를 출력합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "eval"

    def get_command_permission_level(self) -> int:
        return EPermissionLevel.OWNER

    @execute_condition_checker()
    async def execute(self, msg: Message, arguments: list, *args, **kwargs):
        try:
            result = eval(' '.join(arguments), kwargs['main_global'])
        except:
            result = format_exc()

        if result is not None:
            result = repr(result)
            frag_size = TEXT_LENGTH_LIMIT - 8
            for result_split in [result[i:i + frag_size] for i in range(0, len(result), frag_size)]:
                await msg.channel.send('```\n' + result_split + '\n```')
