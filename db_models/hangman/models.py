from db_models.base_model import *
from django.core.validators import MinValueValidator, MaxValueValidator

from db_models.common.models import User, Message
from db_models.words.models import EnglishWord


class HangmanGame(BaseModel):
    HANGMAN_PARTS = 6

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hangman_games')
    state = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(HANGMAN_PARTS)])
    word = models.ForeignKey(EnglishWord, on_delete=models.PROTECT, related_name='hangman_games')
    guesses = models.CharField(max_length=26)
    timestamp = models.DateTimeField(auto_now_add=True)


class HangmanSession(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='hangman_session')
    msg = models.OneToOneField(Message, on_delete=models.SET_NULL, related_name='+', null=True)
    game = models.OneToOneField(HangmanGame, on_delete=models.PROTECT, related_name='hangman_session')
    last_interaction_timestamp = models.DateTimeField(auto_now=True)
