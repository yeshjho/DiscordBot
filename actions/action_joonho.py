from actions.action import *

from nextcord import Message

from common import EPermissionLevel
from helper_functions import *


class ActionJoonho(Action):
    async def on_message(self, msg: Message, **kwargs):
        if "준호" not in msg.content or msg.author.bot:
            return EActionExecuteResult.NO_MATCH

        permission_level = get_permission_level(msg.author.id, msg.guild.id, [role.id for role in msg.author.roles])
        if permission_level >= EPermissionLevel.DEFAULT:
            await msg.channel.send(mention_user(OWNER_ID))

        # TODO: make it universally available and configurable
