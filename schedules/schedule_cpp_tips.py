from random import choice
import discord.utils

from constants import *


class CppTipsContainer:
    def __init__(self):
        with open("database/cpp_tips.txt", encoding='utf-8') as file:
            self.tips = file.read().split('@@@')
        self.tips = [x.strip() for x in self.tips]

    def get_random_tip(self) -> str:
        return choice(self.tips)


cpp_tips_container = CppTipsContainer()


async def publish_random_cpp_tips(bot):
    guild = discord.utils.get(bot.guilds, id=PUBLISH_GUILD_ID)
    channel = discord.utils.get(guild.channels, id=PUBLISH_CHANNEL_ID)

    message = await channel.send(cpp_tips_container.get_random_tip())
    await message.publish()
