from discord import Member, Embed


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
