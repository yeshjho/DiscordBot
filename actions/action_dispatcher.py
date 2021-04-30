from importlib import import_module
from glob import glob

from actions.action import Action, EActionExecuteResult
from constants import *
from helper_functions import *

actions = []

EXCLUDES = ['action_dispatcher.py']
for action_file in glob('actions/*.py'):
    action_file = action_file.split('\\')[1] if '\\' in action_file else action_file.split('/')[1]
    if action_file.startswith('action_') and action_file not in EXCLUDES:
        file_name = action_file.split('.')[0]
        module = import_module('actions.' + file_name)
        class_name = ''.join([c[0].upper() + c[1:] for c in file_name.split('_')])
        actions.append(module.__dict__[class_name]())


async def execute_action(method_name: str, *args, **kwargs):
    for action in actions:
        if not is_method_overriden(Action, action, method_name):
            continue

        execute_result = await action.__getattribute__(method_name)(*args, **kwargs, actions=actions)
        if execute_result is None:
            execute_result = EActionExecuteResult.SUCCESS

        if execute_result == EActionExecuteResult.SUCCESS:
            break
