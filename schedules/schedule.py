import asyncio
from datetime import datetime, timedelta
from typing import Dict

from logger import log_schedule


class Scheduler:
    class Schedule:
        def __init__(self, func, name: str, every: timedelta, *args, **kwargs):
            self.func = func
            self.name: str = name
            self.every: timedelta = every

            self.args = args
            self.kwargs = kwargs

            self.next_execute_timestamp: datetime = datetime.now()

        async def execute(self) -> None:
            self.func(*self.args, **self.kwargs)
            if self.every == timedelta.min:
                self.next_execute_timestamp = datetime.max
                self.abort()
            else:
                self.next_execute_timestamp = datetime.now() + self.every

            log_schedule(self.name, self.next_execute_timestamp)

        def abort(self) -> None:
            del Scheduler.schedules[self.name]

    schedules: Dict[str, Schedule] = {}

    @staticmethod
    def schedule(func, name: str, start_at: datetime, every: timedelta = timedelta.min, *args, **kwargs):
        new_schedule = Scheduler.Schedule(func, name, every, args, kwargs)
        new_schedule.next_execute_timestamp = start_at
        Scheduler.schedules[name] = new_schedule

    @staticmethod
    async def update():
        now: datetime = datetime.now()
        for _, schedule in Scheduler.schedules:
            if schedule.next_execute_timestamp <= now:
                await schedule.execute()

    @staticmethod
    async def main_loop():
        while True:
            await Scheduler.update()
            await asyncio.sleep(1)
