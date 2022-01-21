from typing import Union, List

from nextcord import Guild

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
              'group_join', 'group_remove', 'guild_scheduled_event_create', 'guild_scheduled_event_update',
              'guild_scheduled_event_delete', 'guild_scheduled_event_user_add', 'guild_scheduled_event_user_remove']

    # None if is not guild-related, tuple(arg index, attr name) if is.
    # arg index can be omitted, defaulted to 0.
    # attr name can be omitted, defaulted to 'guild'.
    # attr name can be nested, concat with '/'.
    # if the length of the tuple is >= 3, the attr is considered as a callable and the rest will be passed as arguments.
    #   if the attr is nested, the first attr is assumed as a callable.
    GUILD_GETTERS = dict(zip(EVENTS, [None, None, None, None, None, None,
                                      None, None, None, (), (), (),
                                      (0, '__getitem__/guild', 0), (), (0, 'message/guild'), (0, 'message/guild'), (),
                                      (0, 'message/guild'), None, None,
                                      (), (), (), (),
                                      (), (), (), (0, 'thread/guild'), (0, 'thread/guild'),
                                      (), (0, ''), (), (),
                                      (), (), (), (), (),
                                      (0, 'mutual_guilds'), (0, ''), (0, ''), (0, ''), (), (),
                                      (), (0, ''), (0, ''), (0, ''),
                                      (0, ''), (), (), (),
                                      (), (0, ''), (0, ''), (), (),
                                      None, None, (), (),
                                      (), (), ()]))

    @staticmethod
    def get_guild(method_name: str, args) -> Union[Guild, List[Guild], None]:
        getter = Action.GUILD_GETTERS[method_name]
        if getter is None:
            return None

        index: int
        attributes = []
        attr_args = []
        if len(getter) == 0:
            index = 0
            attributes = ['guild']
        elif len(getter) == 1:
            index = getter[0]
            attributes = ['guild']
        else:
            index = getter[0]
            attributes = getter[1].split('/')
            attr_args = getter[2:]

        to_return = args[index]
        if not attributes:
            return to_return

        to_return = to_return.__getattribute__(attributes[0])
        if attr_args:
            to_return = to_return(*attr_args)
        attributes.pop(0)

        for attr in attributes:
            to_return = to_return.__getattribute__(attr)

        return to_return

    INTENDER_GETTERS = dict(zip(EVENTS, []))
