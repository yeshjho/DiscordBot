from commands.command import *

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

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(dest='mode')

        get_parser = subparsers.add_parser('get')
        get_parser.add_argument('type', choices=['user', 'guild', 'role'])
        get_parser.add_argument('id', type=int)

        set_parser = subparsers.add_parser('set')
        set_parser.add_argument('type', choices=['user', 'guild', 'role'])
        set_parser.add_argument('id', type=int)
        set_parser.add_argument('level', type=int)

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        if not args.mode:
            await msg.channel.send(mention_user(msg.author) + "님의 권한 레벨은 "
                                   + str(permissions.get_permission_level(msg.author)) + "입니다")
            return

        if permissions.get_permission_level(msg.author) < EPermissionLevel.ADMIN:
            return ECommandExecuteResult.NO_PERMISSION

        if args.mode == 'get':
            await msg.channel.send("해당 권한 레벨은 " +
                                   str(permissions.get_permission_level(args.type, args.id)) + "입니다")

        elif args.mode == 'set':
            permissions.set_permission_level(args.type, args.id, args.level)
            await msg.channel.send("해당 권한 레벨을 " + str(args.level) + "로 설정했습니다")

            if IS_TESTING:
                await msg.channel.send("테스트 중이라 새 권한 정보는 유실될 거예요!")

        else:
            raise
