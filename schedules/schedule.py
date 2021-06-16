from abc import ABCMeta, abstractmethod

import asyncio
import datetime


class Scheduler:
    prev_time = datetime.datetime.now()
    current_id = 0
    schedules = {}

    @staticmethod
    def register(schedule, initial_delay: datetime.timedelta) -> int:
        granted_id = Scheduler.current_id
        Scheduler.current_id += 1

        schedule.scheduler_granted_schedule_id = granted_id
        schedule.scheduler_granted_remaining_time = initial_delay
        Scheduler.schedules[granted_id] = schedule
        return granted_id

    @staticmethod
    def remove(schedule_id_or_name: int or str):
        if type(schedule_id_or_name) is int:
            del Scheduler.schedules[schedule_id_or_name]
        else:
            for schedule_id, schedule in Scheduler.schedules:
                if schedule.name == schedule_id:
                    del Scheduler.schedules[schedule_id]
                    break

    @staticmethod
    async def update():
        curr_time = datetime.datetime.now()
        diff = curr_time - Scheduler.prev_time
        Scheduler.prev_time = curr_time

        to_remove = []
        for schedule_id, schedule in Scheduler.schedules.items():
            if schedule.scheduler_granted_remaining_time <= diff:
                result = await schedule.execute()
                if result is None:
                    to_remove.append(schedule_id)
                else:
                    schedule.scheduler_granted_remaining_time = result
            else:
                schedule.scheduler_granted_remaining_time -= diff

        for remove_id in to_remove:
            Scheduler.remove(remove_id)

    @staticmethod
    async def main_loop():
        while True:
            await Scheduler.update()
            await asyncio.sleep(0)


class Schedule(metaclass=ABCMeta):
    # WARNING: schedules are not saved between different execution, meaning awaiting schedules will not be executed
    # when the bot gets downed
    def __init__(self, func, name: str, *args, **kwargs):
        self.func = func
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.schedule_id = None

    @abstractmethod
    async def execute(self) -> datetime.timedelta or None:
        # if returns None, it is removed from the scheduler. else, gets executed after that amount of time
        pass

    def abort(self):
        Scheduler.remove(self.schedule_id)


class RepeatWithInterval(Schedule):
    def __init__(self, func, interval: datetime.timedelta, count: int, name: str, *args, **kwargs):
        super().__init__(func, name, *args, **kwargs)
        self.count = count
        self.interval = interval

    @staticmethod
    def create(func, interval: datetime.timedelta, start_immediately: bool = False, count: int = -1, name: str = "",
               *args, **kwargs) -> int:
        schedule = RepeatWithInterval(func, interval, count, name, *args, **kwargs)
        return Scheduler.register(schedule, datetime.timedelta(0, 0) if start_immediately else interval)

    async def execute(self) -> datetime.timedelta or None:
        await self.func(*self.args, **self.kwargs)
        self.count -= 1
        return None if self.count == 0 else self.interval


class ExecuteAfter(RepeatWithInterval):
    @staticmethod
    def create(func, delay: datetime.timedelta, name: str = "", *args, **kwargs) -> int:
        schedule = RepeatWithInterval(func, delay, 1, name, *args, **kwargs)
        return Scheduler.register(schedule, delay)


class RepeatAtCertainTime(Schedule):
    # It could be done with RepeatWithInterval,
    # but didn't because of the accumulation of the small errors every time it is called
    def __init__(self, func, time: datetime.time, count: int, name: str, *args, **kwargs):
        super().__init__(func, name, *args, **kwargs)
        self.time = time
        self.count = count

    @staticmethod
    def get_remaining_time(time: datetime.time) -> datetime.timedelta:
        tomorrow_time = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(1), time)
        now = datetime.datetime.now()
        diff = tomorrow_time - now
        if diff >= datetime.timedelta(1):
            diff -= datetime.timedelta(1)
        return diff

    @staticmethod
    def create(func, time: datetime.time, count: int = -1, name: str = "", *args, **kwargs) -> int:
        schedule = RepeatAtCertainTime(func, time, count, name, *args, **kwargs)
        return Scheduler.register(schedule, RepeatAtCertainTime.get_remaining_time(time))

    async def execute(self) -> datetime or None:
        await self.func(*self.args, **self.kwargs)
        self.count -= 1
        return RepeatAtCertainTime.get_remaining_time(self.time)
