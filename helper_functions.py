from nextcord import Member, Embed

from typing import List

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


def get_permission_level(user_id: int, guild_id: int = None, role_ids: List[int] = None):
    from db_models.common import models
    from django.core.exceptions import ObjectDoesNotExist

    if role_ids is None:
        role_ids = []

    user, _ = models.User.objects.get_or_create(id=user_id)
    permission_levels = [models.UserPermission.objects.get_or_create(user=user)[0].level]

    if guild_id:
        guild, _ = models.Guild.objects.get_or_create(id=guild_id)
        try:
            permission_levels.append(models.GuildPermission.objects.get(guild__id=guild_id).level)
        except ObjectDoesNotExist:
            pass

        roles = []
        for role_id in role_ids:
            role_, _ = models.Role.objects.get_or_create(id=role_id, guild=guild)
            roles.append(role_)
            try:
                permission_levels.append(models.RolePermission.objects.get(role__id=role_id).level)
            except ObjectDoesNotExist:
                pass

    return max(permission_levels)


class MultipleUserException(Exception):
    pass


def get_user_id(nick_or_mention_or_id, guild=None) -> int or List[int]:
    if nick_or_mention_or_id.isnumeric():
        return int(nick_or_mention_or_id)
    elif nick_or_mention_or_id.startswith("<@!") and nick_or_mention_or_id.endswith('>'):
        return int(nick_or_mention_or_id[3:-1])
    elif guild:
        candidates = list(filter(lambda x: not x.bot and x.display_name == nick_or_mention_or_id,
                                 await guild.fetch_members().flatten()))
        if len(candidates) != 1:
            raise MultipleUserException()
        return candidates[0].id
    else:
        raise
