from schedules.schedule import *
from schedules.schedule_cpp_tips import *


def schedule_initial(*args, **kwargs):
    RepeatAtCertainTime.create(publish_random_cpp_tips, datetime.time(15), -1, "CppTips", kwargs['bot'])
