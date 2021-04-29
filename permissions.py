from sys import maxsize

from discord import Member


class EPermissionLevel:
    BANNED = -1
    ALL = 0

    OWNER = maxsize


def get_permission_level(user):
    user_type = type(user)
    user_id = None
    if user_type is int:
        user_id = user
    elif user_type is Member:
        user_id = user.id

    if user_id is None:
        return EPermissionLevel.ALL

    if user_id == 353886187879923712:
        return EPermissionLevel.OWNER

    return EPermissionLevel.ALL
