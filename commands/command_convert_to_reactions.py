import discord.errors

from commands.command import *

from discord import errors

from helper_functions import *


class CommandConvertToReactions(Command):
    """
    <letters>
    답장 원본 메시지에 letters를 글자 이모지로 분해해 반응
    답장하는 원본 메시지에 letters를 가능한 이모지로 분해해 반응해 줍니다.
    예) `react abc -> 원본 메시지에 :regional_indicator_a:, :regional_indicator_b:, :regional_indicator_c:를 반응
    """
    def __init__(self):
        super().__init__()

        self.letter_icon_map = {'a': ['🇦', '🅰️'], 'b': ['🇧', '🅱️'], 'c': ['🇨'], 'd': ['🇩'], 'e': ['🇪'],
                                'f': ['🇫'], 'g': ['🇬'], 'h': ['🇭'], 'i': ['🇮', 'ℹ️'], 'j': ['🇯'], 'k': ['🇰'],
                                'l': ['🇱'], 'm': ['🇲'], 'n': ['🇳'], 'o': ['🇴', '🅾️'], 'p': ['🇵', '🅿️'],
                                'q': ['🇶'], 'r': ['🇷'], 's': ['🇸'], 't': ['🇹'], 'u': ['🇺'], 'v': ['🇻'],
                                'w': ['🇼'], 'x': ['🇽'], 'y': ['🇾'], 'z': ['🇿'],
                                '0': ['0️⃣'], '1': ['1️⃣'], '2': ['2️⃣'], '3': ['3️⃣'], '4': ['4️⃣'], '5': ['5️⃣'],
                                '6': ['6️⃣'], '7': ['7️⃣'], '8': ['8️⃣'], '9': ['9️⃣'], '10': ['🔟'],
                                'ab': ['🆎'], 'cl': ['🆑'], 'ok': ['🆗'], 'ng': ['🆖'], 'id': ['🆔'], 'sos': ['🆘'],
                                'vs': ['🆚'], 'cool': ['🆒'], 'new': ['🆕'], 'free': ['🆓'], 'abc': ['🔤']}
        self.skip_letters = [' ']

    def get_command_str(self) -> str:
        return "react"

    @execute_condition_checker()
    async def execute(self, msg: Message, arguments: list, *args, **kwargs):
        if not msg.reference:
            await msg.delete()
            return EExecuteResult.SYNTAX_ERROR

        original_msg = await msg.channel.fetch_message(msg.reference.message_id)
        if not original_msg:
            await msg.delete()
            return EExecuteResult.CUSTOM_ERROR, mention_user(msg.author) + " 원본 메시지가 없어졌어요!"

        await msg.delete()

        s = ''.join(arguments).lower()
        letter_icon_map_copy = self.letter_icon_map.copy()
        icon_name_list = []

        current_to_find = ''
        for c in s:
            if c in self.skip_letters:
                continue

            current_to_find += c
            if current_to_find in letter_icon_map_copy and len(letter_icon_map_copy[current_to_find]) > 0:
                icon_name_list.append(letter_icon_map_copy[current_to_find][0])
                letter_icon_map_copy[current_to_find] = letter_icon_map_copy[current_to_find][1:]
                current_to_find = ''

        if current_to_find != '':
            return EExecuteResult.CUSTOM_ERROR, mention_user(msg.author) + " 이모지가 부족해요!"
        else:
            try:
                for icon_name in icon_name_list:
                    await original_msg.add_reaction(icon_name)
            except discord.errors.Forbidden:
                pass
