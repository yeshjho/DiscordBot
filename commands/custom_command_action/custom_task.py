from asyncio import TimeoutError
from datetime import datetime, timedelta
from itertools import chain
from typing import Tuple, Optional

from nextcord import Message
import nextcord.ext.commands.errors

from .custom_task_argument import *
from helper_functions import *
from schedules.schedule import Scheduler


# its value is used directly by the db, don't change the order
class ECustomTaskType(IntEnum):
    SEND_MESSAGE = auto()
    MENTION_USER = auto()
    REPEAT = auto()
    TOGGLE_MUTE = auto()
    TOGGLE_DEAF = auto()


class NotEnoughUserArgumentException(Exception):
    pass


class NoChannelException(Exception):
    pass


class ArgumentParseException(Exception):
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

    @abstractmethod
    def get_format_string(self, *args) -> str:
        pass

    async def get_arguments_input(self, msg: Message, embed: Embed, bot: Client, user: User, channel: TextChannel,
                                  is_for_command: bool, args_out: List[str]) -> bool:
        if is_for_command:
            await channel.send('참고: arg0, arg1과 같은 식으로 명령어가 사용될 때 받는 인자를 표시할 수 있습니다\n'
                               '예) `arg0`을 입력해두면 `(명령어) lorem`과 같은 식으로 명령어가 사용됐을 시 해당 인자에 `lorem`이 들어감')
        for arg in self.arguments:
            try:
                if not arg.no_prompt:
                    await channel.send('**`' + arg.arg_name + '`**' + "에 대한 인자를 입력하세요")
                value = await arg.get_input(bot, user, channel, msg=msg, embed=embed, args_out=args_out,
                                            custom_tasks=custom_tasks)
                args_out.append(value)
                if not arg.no_prompt:
                    embed.add_field(name=arg.arg_name, value=arg.get_display_str(value, custom_tasks=custom_tasks))
                    await msg.edit(embed=embed)
            except (nextcord.errors.HTTPException, TimeoutError):
                return False
        return True

    async def execute(self, stored_args: Tuple[str, ...], user_args: Tuple[str, ...], channel: Optional[TextChannel],
                      **kwargs):
        args = []
        for i, arg in enumerate(stored_args):
            result = re.search(r'^arg(\d+)$', arg)
            if result:
                index = int(result[1])
                if len(user_args) < index + 1:
                    raise NotEnoughUserArgumentException
                try:  # check parse error
                    self.arguments[i].parse(user_args[index])
                except:
                    raise ArgumentParseException
                args.append(user_args[index])
            elif arg == 'channel':
                if not channel:
                    raise NoChannelException
                args.append(channel)
            else:
                args.append(arg)

        def arg_parser(j: int, argument: CustomTaskArgument):
            if argument.type == ECustomTaskArgumentType.TASK:
                return argument.parse(*args[j:], custom_tasks=custom_tasks)
            else:
                return argument.parse(args[j]),
        return await self.execute_inner(*chain(*[arg_parser(x, y) for x, y in enumerate(self.arguments)]), **kwargs)

    @abstractmethod
    async def execute_inner(self, *args, **kwargs):
        pass


class CustomTaskSendMessage(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.SEND_MESSAGE

    @property
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        return ECustomTaskArgumentType.CHANNEL, ECustomTaskArgumentType.TEXT

    def get_format_string(self, *args) -> str:
        return '해당 채널에 `{1}` 메시지를 전송'.format(*args)

    async def execute_inner(self, *args, **kwargs):
        channel, text = args
        await channel.send(text)


class CustomTaskMentionUser(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.MENTION_USER

    @property
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        return ECustomTaskArgumentType.CHANNEL, ECustomTaskArgumentType.USER

    def get_format_string(self, *args) -> str:
        return '해당 채널에 <@{1}> 유저를 멘션'.format(*args)

    async def execute_inner(self, *args, **kwargs):
        channel, user = args
        await channel.send(mention_user(user))


class CustomTaskRepeat(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.REPEAT

    @property
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        return ECustomTaskArgumentType.CHANNEL, ECustomTaskArgumentType.INT, ECustomTaskArgumentType.INT, \
               ECustomTaskArgumentType.TASK

    def get_format_string(self, *args) -> str:
        custom_task = custom_tasks[ECustomTaskType(int(args[-1]))]
        return '"{0}" 작업을 {2}초 간격으로 {1}번 반복\n'.format(custom_task.task_name, args[1], args[2]) + \
               custom_task.get_format_string(*args[3:-1])

    async def execute_inner(self, *args, **kwargs):
        channel, count, interval, *task_args, task = args

        schedule_name = str(channel.id) + kwargs['command_str']

        if schedule_name in Scheduler.schedules:
            Scheduler.schedules[schedule_name].abort()
        else:
            async def f():
                await custom_tasks[task].execute_inner(*task_args, **kwargs)
            Scheduler.schedule(f, schedule_name, datetime.now(), timedelta(seconds=interval), count)


class CustomTaskToggleMute(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.TOGGLE_MUTE

    @property
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        return ECustomTaskArgumentType.CHANNEL, ECustomTaskArgumentType.USER

    def get_format_string(self, *args) -> str:
        return '<@{1}> 유저의 마이크 음소거를 토글'.format(*args)

    async def execute_inner(self, *args, **kwargs):
        channel, user_id = args

        user = await channel.guild.fetch_member(user_id)
        await user.edit(mute=not user.voice.mute)


class CustomTaskToggleDeaf(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.TOGGLE_DEAF

    @property
    def required_args(self) -> Tuple[ECustomTaskArgumentType, ...]:
        return ECustomTaskArgumentType.CHANNEL, ECustomTaskArgumentType.USER

    def get_format_string(self, *args) -> str:
        return '<@{1}> 유저의 헤드셋 음소거를 토글'.format(*args)

    async def execute_inner(self, *args, **kwargs):
        channel, user_id = args

        user = await channel.guild.fetch_member(user_id)
        await user.edit(deafen=not user.voice.deaf)


custom_tasks = dict([(action.type, action) for action in [
    CustomTaskSendMessage("메시지 전송", '해당 채널에 정해진 메시지를 전송합니다',
                          CustomTaskArgumentChannel(''), CustomTaskArgumentText("메시지 내용")),
    CustomTaskMentionUser("유저 멘션", '해당 채널에 정해진 유저를 멘션합니다',
                          CustomTaskArgumentChannel(''), CustomTaskArgumentUser("멘션할 유저")),
    CustomTaskRepeat("작업 반복", '해당 채널에 정해진 작업을 반복합니다',
                     CustomTaskArgumentChannel(''), CustomTaskArgumentInt('반복 횟수'), CustomTaskArgumentInt('반복 간격'),
                     CustomTaskArgumentTask('반복할 작업')),
    CustomTaskToggleMute("마이크 음소거 토글", '정해진 유저의 마이크 음소거를 토글합니다', CustomTaskArgumentChannel(''),
                         CustomTaskArgumentUser("토글할 유저")),
    CustomTaskToggleDeaf("헤드셋 음소거 토글", '정해진 유저의 헤드셋 음소거를 토글합니다', CustomTaskArgumentChannel(''),
                         CustomTaskArgumentUser("토글할 유저"))
]])
