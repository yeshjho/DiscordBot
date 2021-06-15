import discord.utils

from constants import *


async def publish_random_cpp_tips(bot):
    guild = discord.utils.get(bot.guilds, id=PUBLISH_GUILD_ID)
    channel = discord.utils.get(guild.channels, id=PUBLISH_CHANNEL_ID)

    message = await channel.send("asdf")
    await message.publish()
