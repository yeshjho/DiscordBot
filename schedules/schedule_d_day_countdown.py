import nextcord.utils
from nextcord import Guild, Member

from constants import *


async def change_d_day_nick(bot):
    guild: Guild = nextcord.utils.get(bot.guilds, id=552775664130981888)
    member: Member = await guild.fetch_member(OWNER_ID)
    d_day = member.nick.split('/')
    try:
        await member.edit(nick=str(int(d_day[0]) + 1) + '/' + d_day[1])
    except nextcord.errors.Forbidden:
        pass
