from importlib import import_module
from glob import glob

from actions.action import *
from helper_functions import *
from logger import log_action

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
        if not hasattr(action, method_name):
            continue

        execute_result = await action.__getattribute__(method_name)(*args, **kwargs)
        additional_args = ()
        if type(execute_result) is tuple:
            if not isinstance(execute_result[0], EActionExecuteResult):
                additional_args = execute_result
                execute_result = EActionExecuteResult.SUCCESS
            else:
                additional_args = execute_result[1:]
                execute_result = execute_result[0]

        if execute_result is None:
            execute_result = EActionExecuteResult.SUCCESS

        if execute_result != EActionExecuteResult.NO_MATCH:
            log_action(action.__class__.__name__, execute_result, additional_args)
