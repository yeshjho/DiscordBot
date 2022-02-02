from abc import ABCMeta, abstractmethod
from enum import IntEnum, auto

from nextcord import TextChannel, Client, User, Interaction, ButtonStyle
from nextcord.ui import Button, View, Select


class ECustomTaskArgumentType(IntEnum):
    CHANNEL = auto()
    TEXT = auto()
    USER = auto()
    TASK = auto()
    INT = auto()


class CustomTaskArgument(metaclass=ABCMeta):
    def __init__(self, arg_name: str):
        self.arg_name: str = arg_name

    @property
    @abstractmethod
    def type(self) -> ECustomTaskArgumentType:
        pass

    # gets an input from user and returns a string storeable in the db
    @abstractmethod
    async def get_input(self, bot: Client, user: User, channel: TextChannel, **kwargs) -> str:
        pass

    # takes the argument stored in the db and reinterprets to its type
    @abstractmethod
    def parse(self, arg: str):
        pass

    @property
    def no_prompt(self) -> bool:
        return False


class CustomTaskArgumentChannel(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.CHANNEL

    # special case
    async def get_input(self, bot: Client, user: User, channel: TextChannel, **kwargs) -> str:
        return 'channel'

    # special case, arg won't be a str but a channel object itself
    def parse(self, arg: str):
        return arg

    @property
    def no_prompt(self) -> bool:
        return True


class CustomTaskArgumentText(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.TEXT

    async def get_input(self, bot: Client, user: User, channel: TextChannel, **kwargs) -> str:
        return (await bot.wait_for('message', check=lambda x: x.author.id == user.id, timeout=60)).content

    def parse(self, arg: str):
        return arg


class CustomTaskArgumentUser(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.USER

    async def get_input(self, bot: Client, user: User, channel: TextChannel, **kwargs) -> str:
        mention = (await bot.wait_for('message', check=lambda x: x.author.id == user.id and
                                                              x.content.startswith("<@") and x.content.endswith('>'),
                                      timeout=60)).content
        return ''.join(filter(lambda x: x.isdigit(), mention))

    def parse(self, arg: str):
        return int(arg)


class ArgumentTaskConfirmButton(Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.primary, label='선택 (2번 눌러주세요)')
        self.selected_task = -1

    async def callback(self, interaction: Interaction):
        values = self.view.children[0].values
        self.selected_task = int(values[0] if values else '1')


class CustomTaskArgumentTask(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.TASK

    async def get_input(self, bot: Client, user: User, channel: TextChannel, **kwargs) -> str:
        view = View()
        select = Select()

        custom_tasks = kwargs['custom_tasks']
        _, task = list(custom_tasks.items())[0]
        select.add_option(label=task.task_name, value=str(int(task.type)),
                          description=task.task_desc, default=True)
        for _, task in list(custom_tasks.items())[1:]:
            if task.task_name not in ['작업 반복']:  # couldn't use task.type due to cyclic import
                select.add_option(label=task.task_name, value=str(int(task.type)),
                                  description=task.task_desc)
        view.add_item(select)
        button = ArgumentTaskConfirmButton()
        view.add_item(button)
        msg_id = (await channel.send('작업 목록', view=view)).id

        await bot.wait_for('interaction', check=lambda x: x.message.id == msg_id and button.selected_task != -1)
        task_id = button.selected_task
        await custom_tasks[task_id].get_arguments_input(kwargs['msg'], kwargs['embed'],
                                                        bot, user, channel, False, kwargs['args_out'])

        return str(task_id)

    def parse(self, *args: str, **kwargs):
        custom_tasks = kwargs['custom_tasks']
        task_id = int(args[-1])
        custom_task = custom_tasks[task_id]
        task_args = [x.parse(y) for x, y in zip(custom_task.arguments, args)]
        return *task_args, task_id


class CustomTaskArgumentInt(CustomTaskArgument):
    @property
    def type(self) -> ECustomTaskArgumentType:
        return ECustomTaskArgumentType.INT

    async def get_input(self, bot: Client, user: User, channel: TextChannel, **kwargs) -> str:
        return (await bot.wait_for('message', check=lambda x: x.author.id == user.id and x.content.isdigit(),
                                   timeout=60)).content

    def parse(self, arg: str):
        return int(arg)
