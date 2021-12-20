from common import EActionExecuteResult


class Action:
    EVENTS = ['connect', 'shard_connect', 'disconnect', 'shard_disconnect', 'ready', 'shard_ready',
              'resumed', 'shard_resumed', 'socket_event_type', 'typing', 'message', 'message_delete',
              'bulk_message_delete', 'message_edit', 'reaction_add', 'reaction_remove', 'reaction_clear',
              'reaction_clear_emoji', 'private_channel_update', 'private_channel_pins_update',
              'guild_channel_delete', 'guild_channel_create', 'guild_channel_update', 'guild_channel_pins_update',
              'thread_join', 'thread_remove', 'thread_delete', 'thread_member_join', 'thread_member_remove',
              'thread_update', 'guild_integrations_update', 'integration_create', 'integration_update',
              'webhooks_update', 'member_join', 'member_remove', 'member_update', 'presence_update',
              'user_update', 'guild_join', 'guild_remove', 'guild_update', 'guild_role_create', 'guild_role_delete',
              'guild_role_update', 'guild_emojis_update', 'guild_stickers_update', 'guild_available',
              'guild_unavailable', 'voice_state_update', 'stage_instance_create', 'stage_instance_delete',
              'stage_instance_update', 'member_ban', 'member_unban', 'invite_create', 'invite_delete',
              'group_join', 'group_remove']

    def __init__(self):
        def default_func(this, *args, **kwargs):
            pass

        for event in Action.EVENTS:
            self.__setattr__('on_' + event, default_func.__get__(self))
