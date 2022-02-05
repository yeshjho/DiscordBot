import asyncio
import inspect
from datetime import datetime, timedelta
from typing import Dict

from logger import log_schedule


class Scheduler:
    class Schedule:
        def __init__(self, func, name: str, every: timedelta, count: int, *args, **kwargs):
            self.func = func
            self.name: str = name
            self.every: timedelta = every
            self.count = count

            self.args = args
            self.kwargs = kwargs

            self.next_execute_timestamp: datetime = datetime.now()
            self.should_abort = False

        async def execute(self) -> None:
            log_schedule(self.name, self.next_execute_timestamp)

            if inspect.iscoroutinefunction(self.func):
                await self.func(*self.args, **self.kwargs)
            else:
                self.func(*self.args, **self.kwargs)

            self.count -= 1
            if self.count == 0:  # making negative count values loop forever
                self.abort()

            if self.every == timedelta.min:
                self.next_execute_timestamp = datetime.max
                self.abort()
            else:
                self.next_execute_timestamp = datetime.now() + self.every

        def abort(self) -> None:
            self.should_abort = True

    schedules: Dict[str, Schedule] = {}

    @staticmethod
    def schedule(func, name: str, start_at: datetime, every: timedelta = timedelta.min, count: int = -1,
                 *args, **kwargs):
        new_schedule = Scheduler.Schedule(func, name, every, count, *args, **kwargs)
        new_schedule.next_execute_timestamp = start_at
        Scheduler.schedules[name] = new_schedule

    @staticmethod
    async def update():
        to_execute = []
        to_remove = []

        now: datetime = datetime.now()
        for name, schedule in Scheduler.schedules.items():
            if schedule.should_abort:
                to_remove.append(name)
            elif schedule.next_execute_timestamp <= now:
                to_execute.append(schedule.execute())

        await asyncio.gather(*to_execute, return_exceptions=True)

        for name in to_remove:
            del Scheduler.schedules[name]

    @staticmethod
    async def main_loop():
        while True:
            await Scheduler.update()
            await asyncio.sleep(1)
