from commands.command import *

import discord

from helper_functions import *


class CommandPermission(Command):
    """
    [<get|set> <user|guild|role> <id> [level]]
    권한 레벨을 조회/설정
    아무 인자도 없으면 자신의 권한 레벨을 조회합니다.
    get이면 있으면 해당 id의 유저/서버/역할의 레벨을 조회합니다. set이면 level로 설정합니다.
    """

    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "permission"

    @execute_condition_checker()
    async def execute(self, msg: Message, arguments: list, *args, **kwargs):
        len_ = len(arguments)
        if len_ == 0:
            await msg.channel.send(mention_user(msg.author) + "님의 권한 레벨은 "
                                   + str(permissions.get_permission_level(msg.author)) + "입니다")
            return

        elif len_ >= 3:
            if permissions.get_permission_level(msg.author) < EPermissionLevel.ADMIN:
                return ECommandExecuteResult.NO_PERMISSION

            mode = arguments[0]
            target_type = arguments[1]
            id_ = int(arguments[2])
            if target_type not in ["user", "guild", "role"]:
                return ECommandExecuteResult.SYNTAX_ERROR

            if mode == 'get':
                await msg.channel.send("해당 권한 레벨은 " +
                                       str(permissions.get_permission_level(target_type, id_)) + "입니다")
            elif mode == 'set':
                if len_ < 4:
                    return ECommandExecuteResult.SYNTAX_ERROR

                level = int(arguments[3])

                permissions.set_permission_level(target_type, id_, level)
                await msg.channel.send("해당 권한 레벨을 " + str(level) + "로 설정했습니다")

        else:
            return ECommandExecuteResult.SYNTAX_ERROR
