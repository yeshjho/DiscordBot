from commands.command import *

from nextcord import HTTPException, VoiceChannel


class CommandRoleIntersection(Command):
    """
    <user_or_voice_channel> [user_or_voice_channel]...
    역할 교집합
    멘션된 유저들의 역할의 교집합을 구합니다. 음성 채널을 멘션해 해당 음성 채널에 들어와 있는 모든 유저를 포함할 수 있습니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "common_roles"

    def get_command_alias(self) -> list:
        return ["common_role", 'role_intersection', '공통역할', '공통_역할']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('mentions', nargs='+')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        guild = msg.guild
        members = []
        for arg in args.mentions:
            mention_id = int(''.join([c for c in arg if c.isnumeric()]))
            try:
                members.append(await guild.fetch_member(mention_id))
            except HTTPException:
                try:
                    channel = await guild.fetch_channel(mention_id)
                    if not isinstance(channel, VoiceChannel):
                        raise CommandExecuteError("유저 혹은 음성 채널만 멘션 가능합니다")
                    members += channel.members
                except HTTPException:
                    raise CommandExecuteError("유저 혹은 음성 채널만 멘션 가능합니다")

        if len(members) < 2:
            raise CommandExecuteError("대상 유저가 1명 이하입니다")

        roles = [member.roles for member in members]
        intersection = [role.name for role in set.intersection(*map(set, roles))]
        intersection.remove('@everyone')
        await msg.channel.send('공통 역할: ' + ', '.join(intersection))
