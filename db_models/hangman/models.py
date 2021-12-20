from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from db_models.common.models import User, Message
from db_models.words.models import EnglishWord


class HangmanGame(models.Model):
    HANGMAN_PARTS = 6

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hangman_game')
    state = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(HANGMAN_PARTS)])
    word = models.ForeignKey(EnglishWord, on_delete=models.PROTECT, related_name='hangman_game')
    guesses = models.CharField(max_length=26)


class HangmanSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='hangman_session')
    msg = models.OneToOneField(Message, on_delete=models.SET_NULL, related_name='+', null=True)
    game = models.OneToOneField(HangmanGame, on_delete=models.PROTECT, related_name='hangman_session')
