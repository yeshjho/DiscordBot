import asyncio
from collections import Counter
from io import BytesIO

import discord.utils
from discord import Guild, Emoji
from PIL import Image, ImageFont, ImageDraw

from helper_functions import *
from logger import *


class EmojiContainer:
    def __init__(self):
        self.letter_emoji_map = {'a': ['🇦', '🅰️'], 'b': ['🇧', '🅱️'], 'c': ['🇨'], 'd': ['🇩'], 'e': ['🇪'],
                                 'f': ['🇫'], 'g': ['🇬'], 'h': ['🇭'], 'i': ['🇮', 'ℹ️'], 'j': ['🇯'], 'k': ['🇰'],
                                 'l': ['🇱'], 'm': ['🇲'], 'n': ['🇳'], 'o': ['🇴', '🅾️'], 'p': ['🇵', '🅿️'],
                                 'q': ['🇶'], 'r': ['🇷'], 's': ['🇸'], 't': ['🇹'], 'u': ['🇺'], 'v': ['🇻'],
                                 'w': ['🇼'], 'x': ['🇽'], 'y': ['🇾'], 'z': ['🇿'],
                                 '0': ['0️⃣'], '1': ['1️⃣'], '2': ['2️⃣'], '3': ['3️⃣'], '4': ['4️⃣'], '5': ['5️⃣'],
                                 '6': ['6️⃣'], '7': ['7️⃣'], '8': ['8️⃣'], '9': ['9️⃣'],
                                 '!': ['❗', '❕'], '?': ['❓', '❔']}
        self.skip_letters = ['.', ',', '~', '(', ')']
        self.en_guild_ids = [837690275719544904, 837697356380110860, 837690443633524770]
        self.cache_guild_emoji_len = {}
        self.emojis = None  # Use only for emojis other than Korean
        self.ko_emoji_frequency_file_name = "database/ko_emoji_frequency.pickle"
        self.ko_emoji_frequency = load_data(self.ko_emoji_frequency_file_name, {})

        extra_emoji_num = 3
        extra_vowel_num = 2
        for i in range(1, extra_emoji_num + 1):
            for c in "abcdefghijklmnopqrstuvwxyz":
                self.letter_emoji_map[c].insert(0, "#" + c + "_" * i)
        for i in range(extra_emoji_num + 1, extra_emoji_num + extra_vowel_num + 1):
            for c in "aeiou":
                self.letter_emoji_map[c].insert(0, "#" + c + "_" * i)

    @staticmethod
    def is_korean_letter(c: str) -> bool:
        return ord(c) in range(ord('가'), ord('힣') + 1) or ord(c) in range(ord('ㄱ'), ord('ㅣ') + 1)

    def get_emoji(self, name: str or Emoji) -> Emoji:
        if type(name) is str and name.startswith('#'):
            return list(filter(lambda x: x.name == name[1:] and x.guild_id in self.en_guild_ids, self.emojis))[0]
        else:
            return name

    def initialize_cache(self, cache_guilds: list, emojis: list):
        self.emojis = emojis
        self.cache_guild_emoji_len = dict([(guild, len(guild.emojis)) for guild in cache_guilds])
        for cache_guild in cache_guilds:
            for emoji in cache_guild.emojis:
                self.letter_emoji_map[chr(int(emoji.name))] = [emoji]

    async def create_emoji(self, c: str, letters_to_keep: str, target_guild: Guild):
        if target_guild is None:
            for emoji_name, _ in sorted(self.ko_emoji_frequency.items(), key=lambda x: x[1]):
                if chr(emoji_name) not in letters_to_keep:
                    emoji = list(filter(lambda x: x.name == chr(emoji_name)
                                        and discord.utils.get(self.cache_guild_emoji_len.keys(), id=x.guild_id),
                                        self.emojis))
                    if emoji:
                        emoji = emoji[0]
                        target_guild = emoji.guild
                        Logger.log("Deleting emoji", emoji.name, '({})'.format(chr(emoji.name)),
                                   emoji.id, emoji.guild_id)
                        await emoji.delete()
                        break
            else:
                raise

        with Image.open('database/korean_emojis/base.png') as base_img:
            font = ImageFont.truetype("database/korean_emojis/TmoneyRoundWindRegular.ttf", 100, encoding="utf-8")
            text_image = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
            draw_context = ImageDraw.Draw(text_image)
            byte_arr = BytesIO()

            draw_context.text((16, 15), c, fill=(255, 255, 255, 255), font=font)
            emoji_image = Image.alpha_composite(base_img, text_image)
            emoji_image.save(byte_arr, format="PNG")

            emoji = await target_guild.create_custom_emoji(name=str(ord(c)), image=bytes(byte_arr.getvalue()))
            Logger.log("Created emoji", ord(c), '({})'.format(chr(ord(c))), emoji.id, emoji.guild_id)
            self.letter_emoji_map[c] = [emoji]
            return emoji

    def get_target_guild(self):
        for guild, emoji_len in self.cache_guild_emoji_len.items():
            if emoji_len < 50:
                self.cache_guild_emoji_len[guild] += 1
                return guild

    async def get_emojis_for_saying(self, letters: str) -> tuple:
        for c in letters:
            if EmojiContainer.is_korean_letter(c):
                self.ko_emoji_frequency.setdefault(ord(c), 0)
                self.ko_emoji_frequency[ord(c)] += 1
        save_data(self.ko_emoji_frequency_file_name, self.ko_emoji_frequency)

        to_return = []
        to_create = []
        for c in letters:
            if c in self.skip_letters:
                continue

            if c.isspace():
                to_return.append(identity_returner(c))
            elif c in self.letter_emoji_map:
                to_return.append(identity_returner(self.get_emoji(self.letter_emoji_map[c][0])))
            elif EmojiContainer.is_korean_letter(c):
                if c in to_create:
                    to_return.append(identity_returner(c))
                else:
                    to_create.append(c)
                    to_return.append(self.create_emoji(c, letters, self.get_target_guild()))
            else:
                to_return.append(identity_returner(discord.utils.get(self.emojis, id=840907083021025290)))

        result = list(await asyncio.gather(*to_return))
        for index, emoji in enumerate(result):
            if type(emoji) is str and EmojiContainer.is_korean_letter(emoji):
                result[index] = self.get_emoji(self.letter_emoji_map[emoji][0])

        return tuple(result)

    async def get_emojis_for_reaction(self, letters: str) -> tuple:
        for c in letters:
            if EmojiContainer.is_korean_letter(c):
                v = self.ko_emoji_frequency.setdefault(ord(c), 0)
                v += 1
        save_data(self.ko_emoji_frequency_file_name, self.ko_emoji_frequency)

        # TODO: No support for duplicate Korean letter for now
        for dup_letter in [k for k, v in Counter(letters).items() if v > 1]:
            if EmojiContainer.is_korean_letter(dup_letter):
                return ()

        letter_emoji_map_copy = self.letter_emoji_map.copy()

        to_return = []
        to_create = []
        for c in letters:
            if c in self.skip_letters or c.isspace():
                continue

            if len(letter_emoji_map_copy.get(c, [])) > 0:
                to_return.append(identity_returner(self.get_emoji(letter_emoji_map_copy[c][0])))
                letter_emoji_map_copy[c] = letter_emoji_map_copy[c][1:]
            elif EmojiContainer.is_korean_letter(c):
                if c in to_create:
                    to_return.append(identity_returner(c))
                else:
                    to_create.append(c)
                    to_return.append(self.create_emoji(c, letters, self.get_target_guild()))
            else:
                return ()

        result = list(await asyncio.gather(*to_return))
        for index, emoji in enumerate(result):
            if type(emoji) is str and EmojiContainer.is_korean_letter(emoji):
                result[index] = self.get_emoji(self.letter_emoji_map[emoji][0])

        return tuple(result)


emoji_container = EmojiContainer()


async def identity_returner(to_return):
    return to_return
