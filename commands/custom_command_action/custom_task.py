from typing import Tuple, Optional

from re import search

from custom_task_argument import *


class ECustomTaskType(IntEnum):
    SEND_MESSAGE = auto()
    MENTION_USER = auto()

    MAX = auto()


class NotEnoughUserArgumentException(Exception):
    pass


class NoChannelException(Exception):
    pass


class CustomTask(metaclass=ABCMeta):
    def __init__(self, action_name: str, *arguments: CustomTaskArgument):
        self.action_name: str = action_name
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

    def init_generator(self, channel: TextChannel):
        # TODO
        for arg in self.arguments:
            arg.get_input(channel)
            yield

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
        await self.execute_inner([x.parse(y) for x, y in zip(self.arguments, args)])

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

    async def execute_inner(self, *args):
        channel, text = args
        await channel.send(text)


class CustomTaskMentionUser(CustomTask):
    @property
    def type(self) -> ECustomTaskType:
        return ECustomTaskType.MENTION_USER


custom_tasks = dict([(action.type, action) for action in [
    CustomTaskSendMessage("메시지 전송", CustomTaskArgumentChannel(''), CustomTaskArgumentText("메시지 내용")),
    CustomTaskMentionUser("유저 멘션", CustomTaskArgumentChannel(''), )
]])
