from db_models.base_model import *
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from enum import IntEnum, auto

from db_models.common.models import User
from db_models.words.models import EnglishWord

from helper_functions import mention_user, get_enum_list


class EGuessResult(IntEnum):
    ALREADY_USED = 0
    WIN = 1
    LOSE = 2
    NORMAL = 3


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


def validate_lower_case(c: str):
    if c not in 'abcdefghijklmnopqrstuvwxyz':
        raise ValidationError("%(char)s is not a lowercase alphabet", params={'char': c})


class HangmanGame(BaseModel):
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

    def guess(self, c: str) -> EGuessResult:
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


class HangmanBattleGame(BaseModel):
    class EResult(IntEnum):
        PLAYING = auto()
        PLAYER_1_WIN = auto()
        PLAYER_2_WIN = auto()
        DRAW = auto()

    user1 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='hangman_battles1')
    user2 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='hangman_battles2')
    word = models.ForeignKey(EnglishWord, on_delete=models.PROTECT, related_name='hangman_battles')
    state = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(HANGMAN_PARTS)])
    user1_guesses = models.CharField(max_length=26, default="", validators=[validate_lower_case])
    user2_guesses = models.CharField(max_length=26, default="", validators=[validate_lower_case])
    user1_draw_guesses = models.CharField(max_length=20, default="", validators=[validate_lower_case])
    user2_draw_guesses = models.CharField(max_length=20, default="", validators=[validate_lower_case])
    result = models.SmallIntegerField(choices=get_enum_list(EResult), default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def start(self):
        pass
    
    def guess(self, c: str) -> EGuessResult:
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


class HangmanBattleSession(BaseModel):
    class EState(IntEnum):
        FIRST_PLAYER_TURN = auto()
        SECOND_PLAYER_TURN = auto()
        TIE_BREAKER = auto()

    user1 = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='hangman_session1')
    user2 = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, null=True,
                                 related_name='hangman_session2')
    msg_id = models.BigIntegerField()
    game = models.OneToOneField(HangmanBattleGame, on_delete=models.PROTECT, null=True,
                                related_name='hangman_battle_session')
    state = models.SmallIntegerField(choices=get_enum_list(EState), default=1)
    last_interaction_timestamp = models.DateTimeField(auto_now=True)

    def finish(self):
        self.delete()
