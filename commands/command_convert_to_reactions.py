from commands.command import *

import nextcord.errors

from emoji_container import *


class CommandConvertToReactions(Command):
    """
    <letters>
    답장 원본 메시지에 letters를 글자 이모지로 분해해 반응
    답장하는 원본 메시지에 letters를 가능한 이모지로 분해해 반응해 줍니다.
    예) `react abc -> 원본 메시지에 :regional_indicator_a:, :regional_indicator_b:, :regional_indicator_c:를 반응
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "react"

    def get_command_alias(self) -> list:
        return ["re", "반응"]

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('letters', nargs='*')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        if not msg.reference:
            await msg.delete()
            raise CommandExecuteError(mention_user(msg.author),
                                      "답장하는 메시지가 없어요! 반응을 달 메시지를 우클릭->답장한 뒤 명령어를 실행해주세요",
                                      delete_after=2)

        original_msg = await msg.channel.fetch_message(msg.reference.message_id)
        if not original_msg:
            await msg.delete()
            raise CommandExecuteError(mention_user(msg.author), "원본 메시지가 없어졌어요!", delete_after=2)

        await msg.delete()
        emojis = await emoji_container.get_emojis_for_reaction(''.join(args.letters).lower())
        if not emojis:
            raise CommandExecuteError(mention_user(msg.author), "이모지가 부족해요!", delete_after=1)

        try:
            for emoji in emojis:
                await original_msg.add_reaction(emoji)
        except nextcord.errors.Forbidden:
            pass
