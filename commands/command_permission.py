from commands.command import *

from django.core.exceptions import ObjectDoesNotExist
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

    def get_command_alias(self) -> list:
        return ["per", "권한"]

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
        from db_models.common.models import UserPermission, GuildPermission, RolePermission, User, Guild, Role

        if not args.mode:
            await msg.channel.send(mention_user(msg.author) + "님의 권한 레벨은 "
                                   + str(UserPermission.objects.get(user__id=msg.author.id).level) + "입니다")
            return

        if kwargs['permission_level'] < EPermissionLevel.ADMIN:
            return ECommandExecuteResult.NO_PERMISSION

        if args.type == 'user':
            permission_group = UserPermission
            group = User
        elif args.type == 'guild':
            permission_group = GuildPermission
            group = Guild
        else:
            permission_group = RolePermission
            group = Role

        if args.mode == 'get':
            level = None
            try:
                level = permission_group.objects.get(**{args.type + '__id': args.id}).level
            except ObjectDoesNotExist:
                pass
            await msg.channel.send("해당하는 권한 레벨이 없습니다" if level is None else "해당 권한 레벨은 " + str(level) + "입니다")

        elif args.mode == 'set':
            if args.type == 'role':
                guild, _ = Guild.objects.get_or_create(id=msg.author.guild.id)
                group, _ = group.objects.get_or_create(id=args.id, guild=guild)
            else:
                group, _ = group.objects.get_or_create(id=args.id)
            permission_group.objects.update_or_create(**{args.type + '__id': args.id},
                                                      defaults={args.type: group, 'level': args.level})
            await msg.channel.send("해당 권한 레벨을 " + str(args.level) + "로 설정했습니다")

        else:
            raise
