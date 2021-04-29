from commands.command import *

from helper_functions import *


class CommandConvertToReactions(Command):
    def __init__(self):
        super().__init__()

        self.letter_icon_map = {'a': ['🇦', '🅰️'], 'b': ['🇧', '🅱️'], 'c': ['🇨'], 'd': ['🇩'], 'e': ['🇪'],
                                'f': ['🇫'], 'g': ['🇬'], 'h': ['🇭'], 'i': ['🇮', 'ℹ️'], 'j': ['🇯'], 'k': ['🇰'],
                                'l': ['🇱'], 'm': ['🇲'], 'n': ['🇳'], 'o': ['🇴', '🅾️'], 'p': ['🇵', '🅿️'],
                                'q': ['🇶'], 'r': ['🇷'], 's': ['🇸'], 't': ['🇹'], 'u': ['🇺'], 'v': ['🇻'],
                                'w': ['🇼'], 'x': ['🇽'], 'y': ['🇾'], 'z': ['🇿'],
                                '0': ['0️⃣'],
                                '1': ['1️⃣'],
                                '2': ['2️⃣'], '3': ['3️⃣'], '4': ['4️⃣'], '5': ['5️⃣'], '6': ['6️⃣'],
                                '7': ['7️⃣'],
                                '8': ['8️⃣'], '9': ['9️⃣'], '10': ['🔟'], 'ab': ['🆎'], 'cl': ['🆑'],
                                'ok': ['🆗'], 'ng': ['🆖'], 'id': ['🆔'], 'sos': ['🆘'], 'vs': ['🆚'],
                                'cool': ['🆒'],
                                'new': ['🆕'], 'free': ['🆓'], 'abc': ['🔤']}
        self.skip_letters = [' ']

    def get_command_str(self) -> str:
        return "react"

    @execute_condition_checker()
    async def execute(self, msg: Message, command_str: str, arguments: list):
        to_return = AsyncMock()
        to_return.x.return_value = True

        should_skip = False

        if not msg.reference:
            should_skip = True

        original_msg = await msg.channel.fetch_message(msg.reference.message_id)
        if not original_msg:
            should_skip = True

        await msg.delete()
        if should_skip:
            return to_return.x()

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
            return to_return.x()
        else:
            for icon_name in icon_name_list:
                await original_msg.add_reaction(icon_name)

        return to_return.x()
