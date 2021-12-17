from commands.command import *

import nextcord.utils


class CommandPublish(Command):
    """
    <message>
    메시지 발행
    메시지를 발행합니다.
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "publish"

    def get_command_alias(self) -> list:
        return ["발행", "pub"]

    def get_command_permission_level(self) -> int:
        return EPermissionLevel.ADMIN

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('message', nargs='*')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        guild = nextcord.utils.get(kwargs['bot'].guilds, id=PUBLISH_GUILD_ID)
        channel = nextcord.utils.get(guild.channels, id=PUBLISH_CHANNEL_ID)

        await msg.delete()

        message = await channel.send(' '.join(args.message))
        await message.publish()
