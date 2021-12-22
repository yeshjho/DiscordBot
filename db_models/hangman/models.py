from db_models.base_model import *
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from db_models.common.models import User
from db_models.words.models import EnglishWord

from helper_functions import mention_user


class EGuessResult:
    ALREADY_USED = 0
    WIN = 1
    LOSE = 2
    NORMAL = 3


def validate_lower_case(c: str):
    if c not in 'abcdefghijklmnopqrstuvwxyz':
        raise ValidationError("%(char)s is not a lowercase alphabet", params={'char': c})


class HangmanGame(BaseModel):
    HANGMAN_PARTS = 6
    HANGMAN_ARTS = [
        r"""  ┌────────
  |/     |
  |
  |
  |
  |
  |
──┴──""",
        r"""  ┌────────
  |/     |
  |      @
  |
  |
  |
  |
──┴──""",
        r"""  ┌────────
  |/     |
  |      @
  |      |
  |      |
  |
  |
──┴──""",
        r"""  ┌────────
  |/     |
  |      @
  |     /|
  |      |
  |
  |
──┴──""",
        r"""  ┌────────
  |/     |
  |      @
  |     /|\
  |      |
  |
  |
──┴──""",
        r"""  ┌────────
  |/     |
  |      @
  |     /|\
  |      |
  |     /
  |
──┴──""",
        r"""  ┌────────
  |/     |
  |      @
  |     /|\
  |      |
  |     / \
  |
──┴──"""
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hangman_games')
    state = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(HANGMAN_PARTS)])
    word = models.ForeignKey(EnglishWord, on_delete=models.PROTECT, related_name='hangman_games')
    guesses = models.CharField(max_length=26, default="", validators=[validate_lower_case])
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_word_state(self) -> str:
        chars = []
        for c in self.word.word:
            chars.append(c if c in self.guesses else '_')
        return ' '.join(chars).upper()

    def get_character_state(self) -> str:
        chars = []
        for c in 'abcdefghijklmnopqrstuvwxyz':
            chars.append('**' + c + '**' if c not in self.guesses else '~~*' + c + '*~~')
        return ' '.join(chars).upper()

    def get_msg(self) -> str:
        return "{}님의 행맨\n```\n{}\n```\n```{}```\n{}".format(
            mention_user(self.user.id), HangmanGame.HANGMAN_ARTS[self.state],
            self.get_word_state(), self.get_character_state())

    def guess(self, c: str) -> int:
        if c in self.guesses:
            return EGuessResult.ALREADY_USED

        self.guesses += c
        self.save()

        if c not in self.word.word:
            self.state += 1
            self.save()
            if self.state == HangmanGame.HANGMAN_PARTS:
                return EGuessResult.LOSE
        elif all([w in self.guesses for w in self.word.word]):
            return EGuessResult.WIN

        return EGuessResult.NORMAL


class HangmanSession(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='hangman_session')
    msg_id = models.BigIntegerField()
    game = models.OneToOneField(HangmanGame, on_delete=models.PROTECT, related_name='hangman_session')
    last_interaction_timestamp = models.DateTimeField(auto_now=True)

    def finish(self):
        self.delete()
