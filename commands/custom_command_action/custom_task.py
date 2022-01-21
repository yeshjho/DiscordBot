from asyncio import TimeoutError
from re import search
from typing import Tuple, Optional

import nextcord.ext.commands.errors

from .custom_task_argument import *


# its value is used directly by the db, don't change the order
class ECustomTaskType(IntEnum):
    SEND_MESSAGE = auto()
    MENTION_USER = auto()


class NotEnoughUserArgumentException(Exception):
    pass


class NoChannelException(Exception):
    pass


class CustomTask(metaclass=ABCMeta):
    def __init__(self, task_name: str, task_desc: str, *arguments: CustomTaskArgument):
        self.task_name: str = task_name
        self.task_desc: str = task_desc
        self.arguments: Tuple[CustomTaskArgument, ...] = arguments

        assert len(self.arguments) == len(self.required_args) and \
               all([required_type == arg.type for required_type, arg in zip(self.required_args, self.arguments)])

    @property
    @abstractmethod
    def type(self) -> ECustomTaskType:
        pass

    @property
    @abstractmethod
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        pass

    @property
    @abstractmethod
    def format_string(self) -> str:
        pass

    async def get_arguments_input(self, title: str, bot: Client, user: User, channel: TextChannel,
                                  is_for_command: bool) -> Optional[List[str]]:
        embed = get_embed(title, '작업: ' + self.task_name)
        msg = await channel.send(embed=embed)
        if is_for_command:
            await channel.send('참고: arg0, arg1과 같은 식으로 명령어가 사용될 때 받는 인자를 표시할 수 있습니다\n'
                               '예) `arg0`을 입력해두면 `(명령어) lorem`과 같은 식으로 명령어가 사용됐을 시 해당 인자에 `lorem`이 들어감')
        args = []
        for arg in self.arguments:
            try:
                if not arg.no_prompt:
                    await channel.send('**`' + arg.arg_name + '`**' + "에 대한 인자를 입력하세요")
                value = await arg.get_input(bot, user, channel)
                args.append(value)
                if not arg.no_prompt:
                    embed.add_field(name=arg.arg_name, value=value)
                    await msg.edit(embed=embed)
            except (nextcord.errors.HTTPException, TimeoutError):
                return
        return args

    async def execute(self, stored_args: Tuple[str, ...], user_args: Tuple[str, ...], channel: Optional[TextChannel]):
        args = []
        for arg in stored_args:
            result = search(r'^arg(\d+)$', arg)
            if result:
                index = int(result[1])
                if len(user_args) < index + 1:
                    raise NotEnoughUserArgumentException
                args.append(user_args[index])
            elif arg == 'channel':
                if not channel:
                    raise NoChannelException
                args.append(channel)
            else:
                args.append(arg)
        return await self.execute_inner(*[x.parse(y) for x, y in zip(self.arguments, args)])

    @abstractmethod
    async def execute_inner(self, *args):
        pass


class CustomTaskSendMessage(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.SEND_MESSAGE

    @property
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        return ECustomTaskArgumentType.CHANNEL, ECustomTaskArgumentType.TEXT

    @property
    def format_string(self) -> str:
        return '해당 채널에 `{1}` 메시지를 전송'

    async def execute_inner(self, *args):
        channel, text = args
        await channel.send(text)


class CustomTaskMentionUser(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.MENTION_USER

    @property
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        return ECustomTaskArgumentType.CHANNEL, ECustomTaskArgumentType.USER_MENTION

    @property
    def format_string(self) -> str:
        return '해당 채널에 {1} 유저를 멘션'

    async def execute_inner(self, *args):
        channel, mention = args
        await channel.send(mention)


custom_tasks = dict([(action.type, action) for action in [
    CustomTaskSendMessage("메시지 전송", '해당 채널에 정해진 메시지를 전송합니다',
                          CustomTaskArgumentChannel(''), CustomTaskArgumentText("메시지 내용")),
    CustomTaskMentionUser("유저 멘션", '해당 채널에 정해진 유저를 멘션합니다',
                          CustomTaskArgumentChannel(''), CustomTaskArgumentUserMention("멘션할 유저")),
]])
