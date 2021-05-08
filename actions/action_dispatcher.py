from importlib import import_module
from glob import glob

from actions.action import *
from common import EActionExecuteResult
from helper_functions import *

actions = []

EXCLUDES = ['action_dispatcher']
for action_file in glob('actions/**/*.py', recursive=True):
    module_name = ''.join(action_file.split('.')[:-1]).replace('\\', '.').replace('/', '.')
    file_name = module_name.split('.')[-1]
    if file_name.startswith('action_') and file_name not in EXCLUDES:
        module = import_module(module_name)
        class_name = ''.join([c[0].upper() + c[1:] for c in file_name.split('_')])
        actions.append(module.__dict__[class_name]())


async def execute_action(method_name: str, *args, **kwargs):
    for action in actions:
        if not is_method_overriden(Action, action, method_name):
            continue

        execute_result = await action.__getattribute__(method_name)(*args, **kwargs)
        if execute_result is None:
            execute_result = EActionExecuteResult.SUCCESS
