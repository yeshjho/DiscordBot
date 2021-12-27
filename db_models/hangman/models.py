from db_models.base_model import *
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from enum import IntEnum, auto

from db_models.common.models import User
from db_models.words.models import EnglishWord

from nextcord import Embed

from constants import *
from helper_functions import mention_user, get_enum_list


class EHangmanGuessResult(IntEnum):
    ALREADY_USED = auto()
    WIN = auto()
    LOSE = auto()
    NORMAL = auto()


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
            mention_user(self.user.id), HANGMAN_ARTS[self.state],
            self.get_word_state(), self.get_character_state())

    def guess(self, c: str) -> EHangmanGuessResult:
        if c in self.guesses:
            return EHangmanGuessResult.ALREADY_USED

        self.guesses += c
        self.save()

        to_return = EHangmanGuessResult.NORMAL
        if c not in self.word.word:
            self.state += 1
            self.save()
            if self.state == HANGMAN_PARTS:
                to_return = EHangmanGuessResult.LOSE
        elif all((w in self.guesses for w in self.word.word)):
            to_return = EHangmanGuessResult.WIN

        self.save()
        return to_return


class HangmanSession(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='hangman_session')
    msg_id = models.BigIntegerField()
    game = models.OneToOneField(HangmanGame, on_delete=models.PROTECT, related_name='hangman_session')
    last_interaction_timestamp = models.DateTimeField(auto_now=True)

    def finish(self):
        self.delete()


class EHangmanBattleState(IntEnum):
    FIRST_PLAYER_TURN = auto()
    SECOND_PLAYER_TURN = auto()
    TIE_BREAKER = auto()


class EHangmanBattleGuessResult(IntEnum):
    ALREADY_USED = auto()
    RIGHT = auto()
    WRONG = auto()
    WIN = auto()
    LOSE = auto()


class HangmanBattleGame(BaseModel):
    class EResult(IntEnum):
        PLAYING = auto()
        PLAYER_1_WIN = auto()
        PLAYER_2_WIN = auto()
        DRAW = auto()

    user1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hangman_battles1')
    user2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hangman_battles2')
    word = models.ForeignKey(EnglishWord, on_delete=models.PROTECT, related_name='hangman_battles')
    state = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(HANGMAN_PARTS)])
    user1_guesses = models.CharField(max_length=26, default="", validators=[validate_lower_case])
    user2_guesses = models.CharField(max_length=26, default="", validators=[validate_lower_case])
    user1_draw_guesses = models.CharField(max_length=20, default="", validators=[validate_lower_case])
    user2_draw_guesses = models.CharField(max_length=20, default="", validators=[validate_lower_case])
    result = models.SmallIntegerField(choices=get_enum_list(EResult), default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_user1_guesses(self) -> str:
        return self.user1_guesses + self.user1_draw_guesses

    def get_user2_guesses(self) -> str:
        return self.user2_guesses + self.user2_draw_guesses

    def get_all_guesses(self) -> str:
        return self.get_user1_guesses() + self.get_user2_guesses()

    def get_word_state(self) -> str:
        chars = []
        for c in self.word.word:
            chars.append(c if c in self.get_all_guesses() else '_')
        return ' '.join(chars).upper()

    def get_character_state(self) -> str:
        chars = []
        for c in 'abcdefghijklmnopqrstuvwxyz':
            chars.append('**' + c + '**' if c not in self.get_all_guesses() else '~~*' + c + '*~~')
        return ' '.join(chars).upper()

    def get_msg(self, user1_name: str, user2_name: str, state: EHangmanBattleState) -> (str, Embed):
        embed = Embed(title='{}님과 {}님의 행맨 배틀'.format(user1_name, user2_name))
        embed.set_image(url=FORCE_FULL_WIDTH_IMAGE_URL)

        user1_guesses = self.get_user1_guesses()
        user2_guesses = self.get_user2_guesses()
        embed.add_field(name='{}님이 사용한 글자'.format(user1_name),
                        value=' '.join(user1_guesses) if user1_guesses else EMPTY_LETTER)
        embed.add_field(name='{}님이 사용한 글자'.format(user2_name),
                        value=' '.join(user2_guesses) if user2_guesses else EMPTY_LETTER)

        turn_txt = '현재 {}님의 턴입니다!'.format(mention_user(self.user1.id)
                                          if state == EHangmanBattleState.FIRST_PLAYER_TURN
                                          else mention_user(self.user2.id))
        txt = "```{}```\n```{}```\n{}\n\n{}".format(
            HANGMAN_ARTS[self.state], self.get_word_state(), self.get_character_state(), turn_txt) \
            if self.result == HangmanBattleGame.EResult.PLAYING and state != EHangmanBattleState.TIE_BREAKER else ""  # TODO
        return txt, embed

    def guess(self, c: str, is_first_user: bool) -> EHangmanBattleGuessResult:
        if c in self.get_all_guesses():
            return EHangmanBattleGuessResult.ALREADY_USED

        if is_first_user:
            self.user1_guesses += c
        else:
            self.user2_guesses += c

        if c in self.word.word:
            to_return = EHangmanBattleGuessResult.RIGHT
        else:
            self.state += 1
            to_return = EHangmanBattleGuessResult.WRONG

        if self.state == HANGMAN_PARTS:
            to_return = EHangmanBattleGuessResult.LOSE

        elif all((w in self.get_all_guesses() for w in self.word.word)):
            to_return = EHangmanBattleGuessResult.WIN

        self.save()
        return to_return


class HangmanBattleSession(BaseModel):
    user1 = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hangman_session1')
    user2 = models.OneToOneField(User, on_delete=models.CASCADE, null=True,
                                 related_name='hangman_session2')
    msg_id = models.BigIntegerField()
    game = models.OneToOneField(HangmanBattleGame, on_delete=models.PROTECT, null=True,
                                related_name='hangman_battle_session')
    state = models.SmallIntegerField(choices=get_enum_list(EHangmanBattleState), default=1)
    user1_wrong_count = models.PositiveSmallIntegerField(default=0)
    user2_wrong_count = models.PositiveSmallIntegerField(default=0)
    last_interaction_timestamp = models.DateTimeField(auto_now=True)

    def finish(self, result: HangmanBattleGame.EResult):
        self.game.result = result.value
        self.game.save()
        self.delete()
