from discord import Member, Embed

from constants import *


def mention_user(user: int or Member) -> str:
    user_type = type(user)
    if user_type is int:
        return "<@" + str(user) + ">"
    elif user_type is Member:
        return "<@" + str(user.id) + ">"
    else:
        return ""


def emojify(emote_name: str) -> str:
    return ':' + emote_name + ':'


def get_embed(title: str = '', desc: str = '', color: int = 0x00FCFF) -> Embed:
    embed = Embed()

    embed.title = title
    embed.description = desc
    embed.colour = color

    return embed


async def send_split(channel, msg: str, prefix: str = '', suffix: str = ''):
    frag_size = TEXT_LENGTH_LIMIT - len(prefix) - len(suffix)
    for result_split in [msg[i:i + frag_size] for i in range(0, len(msg), frag_size)]:
        await channel.send(prefix + result_split + suffix)


def is_method_overriden(parent_class, child_object, method_name: str) -> bool:
    return parent_class.__dict__[method_name].__code__ is not child_object.__getattribute__(method_name).__code__
