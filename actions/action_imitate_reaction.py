from actions.action import *

from constants import *


class ActionImitateReaction(Action):
    IMITATE_USER_IDS = [OWNER_ID]

    async def on_reaction_add(self, reaction, user, **kwargs):
        if user.id not in ActionImitateReaction.IMITATE_USER_IDS:
            return EActionExecuteResult.NO_MATCH

        await reaction.message.add_reaction(reaction.emoji)
