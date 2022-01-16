from command import *

from nextcord import Message

from db_models.custom_command_action.models import EAction

from helper_functions import *


async def cc_send_message(msg, arg0, *_):
    await msg.channel.send(' '.join(arg0))


async def cc_mention_user(msg, arg0, arg1, *_):
    await msg.channel.send(mention_user(int(arg0)) + " " + arg1)


class CustomCommand(Command):
    FUNCTIONS = {
        EAction.SEND_MESSAGE: cc_send_message,
        EAction.MENTION_USER: cc_mention_user,
    }

    def __init__(self, command_model_object):
        super().__init__()
        self.model_object = command_model_object

    def get_command_str(self) -> str:
        return self.model_object.command_text

    def get_command_permission_level(self) -> int:
        return self.model_object.permission_level

    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        await CustomCommand.FUNCTIONS[self.model_object.action](msg, self.model_object.arg0, self.model_object.arg1)

    @staticmethod
    def load():
        from db_models.custom_command_action.models import CustomCommand as CommandModel

        for command in CommandModel.objects:
            commands = guild_custom_commands.setdefault(command.guild.id, {})
            commands[command.command_text] = CustomCommand(command)


guild_custom_commands = {}  # guild_id : {command: CustomCommand}


def add_custom_command(guild_id: int, command: CustomCommand):
    command.model_object.save()
    guild_custom_commands.setdefault(guild_id, {})[command.model_object.command_text] = command
