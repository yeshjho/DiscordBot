from commands.command import *

from asyncio import TimeoutError

from nextcord import Interaction, ButtonStyle
from nextcord.ui import Button, View, Select

from .custom_command_action.custom_command import guild_custom_commands, add_custom_command, CustomCommand
from .custom_command_action.custom_task import custom_tasks
from helper_functions import *


class TaskConfirmButton(Button):
    def __init__(self, bot, user, channel, command):
        super().__init__(style=ButtonStyle.primary, label='선택')
        self.bot = bot
        self.user = user
        self.channel = channel
        self.command = command

    async def callback(self, interaction: Interaction):
        from db_models.custom_command_action.models import CustomCommand as CommandModel

        values = self.view.children[0].values
        selected_task = int(values[0] if values else '1')
        await interaction.edit(content='`' + self.command + '` 명령어 생성 중', view=None)

        task_instance = custom_tasks[selected_task]
        embed = get_embed('명령어 ' + self.command, '작업: ' + task_instance.task_name)
        msg = await self.channel.send(embed=embed)
        args = []
        if not await task_instance.get_arguments_input(msg, embed, self.bot, self.user, self.channel, True, args):
            await interaction.send(content='시간 초과!')
            return

        args_dict = dict([('arg' + str(i), arg) for i, arg in enumerate(args)])

        guild_id = self.channel.guild.id
        add_custom_command(guild_id, CustomCommand(CommandModel(guild_id=guild_id, command_text=self.command,
                                                                task=selected_task, **args_dict)))
        await interaction.send(content='생성 완료!')


class CommandCustomCommand(Command):
    """
    [create|edit|remove <command_to_remove>]
    서버 명령어 조회/관리
    이 서버만의 명령어를 조회/생성/수정/삭제합니다. 인자가 없으면 조회합니다.
    """

    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "command"

    def get_command_alias(self) -> list:
        return ["com", 'servercommand', '명령어', '서버명령어']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('mode', nargs='?', choices=['create', 'c', '생성', '만들기', 'edit', 'e', '수정',
                                                        'delete', 'remove', 'd', 'del', 'r', 'rm', '삭제'])
        parser.add_argument('command_to_remove', nargs='?')

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        if not msg.channel.guild:
            raise CommandExecuteError("이 기능은 서버에서만 사용할 수 있습니다!")

        guild = msg.channel.guild

        if not args.mode:
            embed = get_embed(guild.name + ' 서버의 커스텀 명령어')
            for command_str, command in guild_custom_commands[guild.id].items():
                obj = command.model_object
                task = custom_tasks[obj.task]
                embed.add_field(name=command_str, value=task.get_format_string(*obj.get_args()), inline=False)
            embed.set_image(url=FORCE_FULL_WIDTH_IMAGE_URL)
            await msg.channel.send(embed=embed)

        if args.mode in ['create', 'c', '생성', '만들기']:
            try:
                await msg.channel.send("새로 만들 명령어를 입력하세요")
                command = await kwargs['bot'].wait_for('message',
                                                       check=lambda x: x.author.id == msg.author.id and
                                                                       not x.content.startswith(COMMAND_PREFIX) and
                                                                       all([not y.isspace() for y in x.content]),
                                                       timeout=60)
                command = command.content.lower()

            except TimeoutError:
                raise CommandExecuteError("시간이 초과됐습니다")

            if command in guild_custom_commands.get(msg.guild.id, {}):
                raise CommandExecuteError("이미 같은 명령어가 있습니다")

            view = View()
            select = Select()
            _, task = list(custom_tasks.items())[0]
            select.add_option(label=task.task_name, value=str(int(task.type)),
                              description=task.task_desc, default=True)
            for _, task in list(custom_tasks.items())[1:]:
                select.add_option(label=task.task_name, value=str(int(task.type)),
                                  description=task.task_desc)
            view.add_item(select)
            button = TaskConfirmButton(kwargs['bot'], msg.author, msg.channel, command)
            view.add_item(button)
            await msg.channel.send('`' + command + "` 명령어가 할 작업을 선택하세요", view=view)

        if args.mode in ['edit', 'e', '수정']:
            return

        if args.mode in ['delete', 'remove', 'd', 'del', 'r', 'rm', '삭제']:
            if not args.command_to_remove:
                return ECommandExecuteResult.SYNTAX_ERROR

            if args.command_to_remove not in guild_custom_commands.get(msg.guild.id, {}):
                raise CommandExecuteError("이 서버에는 해당 커스텀 명령어가 없습니다!")

            guild_custom_commands.get(msg.guild.id, {})[args.command_to_remove].model_object.delete()
            del guild_custom_commands.get(msg.guild.id, {})[args.command_to_remove]
            await msg.channel.send("`" + args.command_to_remove + "` 명령어를 삭제했습니다")
