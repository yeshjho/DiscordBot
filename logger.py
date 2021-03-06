from datetime import datetime

from common import ECommandExecuteResult, EActionExecuteResult


class Logger:
    @staticmethod
    def log(*text):
        with open('logs/{}.txt'.format(str(datetime.now().date())), 'a+', encoding='utf-8') as log_file:
            log_file.write("[{}] {}\n".format(str(datetime.now()), ' '.join(map(str, text))))


command_execute_result_str = {
    ECommandExecuteResult.SUCCESS: "Success", ECommandExecuteResult.NO_PERMISSION: "No Permission",
    ECommandExecuteResult.SYNTAX_ERROR: "Syntax Error", ECommandExecuteResult.CUSTOM_ERROR: "Custom Error"
}

action_execute_result_str = {
    EActionExecuteResult.SUCCESS: "Success", EActionExecuteResult.NO_PERMISSION: "No Permission"
}


def log_command(command_str: str, msg, result: ECommandExecuteResult, additional_args: list):
    Logger.log("Command {}:".format(command_str),
               "used by {} ({})".format(msg.author.name, msg.author.id),
               "(a.k.a. {})".format(msg.author.nick) if 'nick' in dir(msg.author) and msg.author.nick else "",
               "in {}".format(msg.channel.id),
               "(A channel in guild {}({}))".format(msg.channel.guild.name, msg.channel.guild.id)
               if 'guild' in dir(msg.channel) else
               "(A DM channel)" if 'recipient' in dir(msg.channel) else "(A Group channel)",
               "as {}".format(msg.content),
               "resulted {}".format(command_execute_result_str[result]),
               "({})".format(' '.join(map(str, additional_args))) if len(additional_args) else ""
               )


def log_action(action_name: str, result: EActionExecuteResult, additional_args: list):
    Logger.log("Action {}:".format(action_name),
               "resulted {}".format(action_execute_result_str[result]),
               "({})".format(' '.join(map(str, additional_args))) if len(additional_args) else ""
               )


def log_schedule(schedule_name: str, next_timestamp: datetime):
    Logger.log("Schedule {}:".format(schedule_name),
               "next execute timestamp is {}".format(next_timestamp) if next_timestamp != datetime.max else ""
               )
