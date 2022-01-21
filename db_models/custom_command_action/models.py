from db_models.base_model import *
from db_models.common.models import Guild

from django.core.validators import MaxValueValidator

from commands.custom_command_action.custom_task import ECustomTaskType


class CustomCommand(BaseModel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='custom_commands')
    command_text = models.TextField()
    permission_level = models.IntegerField(default=0)
    task = models.PositiveIntegerField(validators=[MaxValueValidator(ECustomTaskType.MAX - 1)])
    arg0 = models.TextField()
    arg1 = models.TextField(default='')
