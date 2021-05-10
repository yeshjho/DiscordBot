from commands.command import *

from emoji_container import *


class CommandEmoji(Command):
    """
    <letters>
    letters를 글자 이모지로 분해해 출력
    letters를 가능한 이모지로 분해해 출력해 줍니다.
    예) `emoji abc -> :regional_indicator_a:, :regional_indicator_b:, :regional_indicator_c:를 출력
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "emoji"

    def get_command_alias(self) -> list:
        return ["emo", "emote", "이모지", "이모"]

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('letters', nargs='*')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        await msg.delete()
        emojis = await emoji_container.get_emojis_for_saying(' '.join(args.letters).lower())
        await msg.channel.send(''.join(map(str, emojis)))
