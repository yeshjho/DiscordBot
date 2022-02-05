from ..command import *

from nextcord import Message

from .custom_task import custom_tasks, NotEnoughUserArgumentException, ArgumentParseException


class CustomCommand(Command):
    def __init__(self, command_model_object):
        super().__init__()
        self.model_object = command_model_object

    def get_command_str(self) -> str:
        return self.model_object.command_text

    def get_command_permission_level(self) -> int:
        return self.model_object.permission_level

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        try:
            return await custom_tasks[self.model_object.task].execute(self.model_object.get_args(),
                                                                      args.extra_args, msg.channel, **kwargs,
                                                                      command_str=self.get_command_str())
        except NotEnoughUserArgumentException:
            raise CommandExecuteError("명령어를 실행하기 위한 인자가 부족해요!", delete_after=2)

        except ArgumentParseException:
            raise CommandExecuteError("잘못된 인자입니다!", delete_after=2)

    @staticmethod
    def load():
        from db_models.custom_command_action.models import CustomCommand as CommandModel

        for command in CommandModel.objects.all():
            commands = guild_custom_commands.setdefault(command.guild.id, {})
            commands[command.command_text] = CustomCommand(command)


guild_custom_commands = {}  # guild_id : {command: CustomCommand}


def add_custom_command(guild_id: int, command: CustomCommand):
    command.model_object.save()
    guild_custom_commands.setdefault(guild_id, {})[command.model_object.command_text] = command
