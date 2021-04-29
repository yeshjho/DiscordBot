from discord import Member


def mention_user(user: int or Member) -> str:
    user_type = type(user)
    if user_type is int:
        return "<@" + str(user) + ">"
    elif user_type is Member:
        return "<@" + user.id + ">"
    else:
        return ""


def emojify(emote_name: str):
    return ':' + emote_name + ':'
