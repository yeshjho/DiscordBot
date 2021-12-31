from commands.command import *

from random import choice


class CommandPick(Command):
    """
    <Option1> [Option2] [Option3]...
    랜덤 픽
    주어진 옵션 중에서 하나를 랜덤으로 선택해줍니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "pick"

    def get_command_alias(self) -> list:
        return ["choose", 'choice', '선택']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('options', nargs='+')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        await msg.channel.send('추첨 결과: ' + choice(args.options))
