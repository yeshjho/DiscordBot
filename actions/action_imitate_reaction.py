from actions.action import *

from constants import *


class ActionImitateReaction(Action):
    IMITATE_USER_IDS = [OWNER_ID]

    async def on_reaction_add(self, reaction, user, **kwargs):
        if user.bot or user.id not in ActionImitateReaction.IMITATE_USER_IDS:
            return EActionExecuteResult.NO_MATCH

        await reaction.message.add_reaction(reaction.emoji)

        emoji_info = reaction.emoji if isinstance(reaction.emoji, str) else \
            reaction.emoji.name + " ()".format(reaction.emoji.id)
        return "reacted", emoji_info, "following", user.id
