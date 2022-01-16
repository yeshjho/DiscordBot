from enum import IntEnum, auto

from db_models.base_model import *
from db_models.common.models import Guild

from django.core.validators import MaxValueValidator


class EAction(IntEnum):
    SEND_MESSAGE = auto()
    MENTION_USER = auto()

    MAX = auto()


class CustomCommand(BaseModel):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='custom_commands')
    command_text = models.TextField()
    permission_level = models.IntegerField(default=0)
    action = models.PositiveIntegerField(validators=[MaxValueValidator(EAction.MAX - 1)])
    arg0 = models.TextField()
    arg1 = models.TextField(default='')
