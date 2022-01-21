from ..command import *

from nextcord import Message

from custom_task import custom_tasks


class CustomCommand(Command):
    def __init__(self, command_model_object):
        super().__init__()
        self.model_object = command_model_object

    def get_command_str(self) -> str:
        return self.model_object.command_text

    def get_command_permission_level(self) -> int:
        return self.model_object.permission_level

    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        stored_args = (self.model_object.arg0, self.model_object.arg1)
        await custom_tasks[self.model_object.task].execute(stored_args, args.extra_args, msg.channel)

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
