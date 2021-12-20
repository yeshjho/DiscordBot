from schedules.schedule import *
from schedules.schedule_cpp_tips import *


def get_next_hour(hour: int) -> datetime:
    now: datetime = datetime.now()
    now.replace(minute=0, second=0, microsecond=0)
    today_hour = now.replace(hour=hour)
    return today_hour.replace(day=now.day + 1) if now > today_hour else today_hour


def schedule_initial(*args, **kwargs):
    Scheduler.schedule(publish_random_cpp_tips, "CppTips", get_next_hour(15), timedelta(days=1), kwargs['bot'])
