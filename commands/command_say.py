from commands.command import *


class CommandSay(Command):
    """
    <words>
    앵무새
    말을 따라합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "say"

    def get_command_alias(self) -> list:
        return ["말"]

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('words', nargs='*')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        await msg.channel.send(' '.join(args.words))
