from common import EActionExecuteResult


class Action:
    def __init__(self):
        pass

    async def on_typing(self, channel, user, when, **kwargs):
        pass

    async def on_message(self, msg, **kwargs):
        pass

    async def on_message_delete(self, msg, **kwargs):
        pass

    async def on_bulk_message_delete(self, msgs, **kwargs):
        pass

    async def on_message_edit(self, before, after, **kwargs):
        pass

    async def on_reaction_add(self, reaction, user, **kwargs):
        pass

    async def on_reaction_remove(self, reaction, user, **kwargs):
        pass

    async def on_reaction_clear(self, msg, reactions, **kwargs):
        pass

    async def on_reaction_clear_emoji(self, reaction, **kwargs):
        pass

    async def on_private_channel_create(self, channel, **kwargs):
        pass

    async def on_private_channel_delete(self, channel, **kwargs):
        pass

    async def on_private_channel_update(self, before, after, **kwargs):
        pass

    async def on_private_channel_pins_update(self, channel, last_pin, **kwargs):
        pass

    async def on_guild_channel_create(self, channel, **kwargs):
        pass

    async def on_guild_channel_delete(self, channel, **kwargs):
        pass

    async def on_guild_channel_update(self, before, after, **kwargs):
        pass

    async def on_guild_channel_pins_update(self, channel, last_pin, **kwargs):
        pass

    async def on_guild_integrations_update(self, guild, **kwargs):
        pass

    async def on_webhooks_update(self, channel, **kwargs):
        pass

    async def on_member_join(self, member, **kwargs):
        pass

    async def on_member_remove(self, member, **kwargs):
        pass

    async def on_member_update(self, before, after, **kwargs):
        pass

    async def on_user_update(self, before, after, **kwargs):
        pass

    async def on_guild_join(self, guild, **kwargs):
        pass

    async def on_guild_remove(self, guild, **kwargs):
        pass

    async def on_guild_update(self, before, after, **kwargs):
        pass

    async def on_guild_role_create(self, role, **kwargs):
        pass

    async def on_guild_role_delete(self, role, **kwargs):
        pass

    async def on_guild_role_update(self, before, after, **kwargs):
        pass

    async def on_guild_emojis_update(self, guild, before, after, **kwargs):
        pass

    async def on_guild_available(self, guild, **kwargs):
        pass
    
    async def on_guild_unavailable(self, guild, **kwargs):
        pass
    
    async def on_voice_state_update(self, member, before, after, **kwargs):
        pass
    
    async def on_member_ban(self, guild, user, **kwargs):
        pass
    
    async def on_member_unban(self, guild, user, **kwargs):
        pass
    
    async def on_invite_create(self, invite, **kwargs):
        pass
    
    async def on_invite_delete(self, invite, **kwargs):
        pass
    
    async def on_group_join(self, channel, user, **kwargs):
        pass
    
    async def on_group_remove(self, channel, user, **kwargs):
        pass
