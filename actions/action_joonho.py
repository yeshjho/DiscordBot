from actions.action import *

from discord import Message

from helper_functions import *


class ActionJoonho(Action):
    async def on_message(self, msg: Message, **kwargs):
        if "준호" not in msg.content:
            return EActionExecuteResult.NO_MATCH

        await msg.channel.send(mention_user(OWNER_ID))
