from db_models.base_model import *
from db_models.common.models import Guild


class CustomCommand(BaseModel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='custom_commands')
    command_text = models.TextField()
    permission_level = models.IntegerField(default=0)
    task = models.PositiveSmallIntegerField()
    arg0 = models.TextField(default='')
    arg1 = models.TextField(default='')
    arg2 = models.TextField(default='')
    arg3 = models.TextField(default='')
    arg4 = models.TextField(default='')
    arg5 = models.TextField(default='')
    arg6 = models.TextField(default='')
    arg7 = models.TextField(default='')
    arg8 = models.TextField(default='')
    arg9 = models.TextField(default='')

    def get_args(self):
        index = 0
        args = []
        while True:
            arg_name = 'arg' + str(index)
            if not hasattr(self, arg_name):
                break

            value = self.__getattribute__(arg_name)
            if not value:
                break

            args.append(value)
            index += 1

        return args
