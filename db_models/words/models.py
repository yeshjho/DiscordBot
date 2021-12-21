from db_models.base_model import *


class EnglishWord(BaseModel):
    word = models.TextField()


class CustomEmoji(BaseModel):
    letter = models.CharField(max_length=1, primary_key=True)
    times_used = models.PositiveIntegerField(default=0)
