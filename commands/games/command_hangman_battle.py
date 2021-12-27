from commands.command import *

from random import randint

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import nextcord.errors
from nextcord.ui.view import View, Interaction
from nextcord.ui.button import Button, ButtonStyle, button

from helper_functions import *


class JoinView(View):
    def __init__(self, owner_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.enabled = True

    def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id != self.owner_id and self.enabled

    @button(label='참가', style=ButtonStyle.primary)
    def join(self, _: Button, interaction: Interaction):
        from db_models.hangman.models import HangmanBattleGame, HangmanBattleSession, HangmanSession
        from db_models.words.models import EnglishWord

        if not self.enabled:
            return
        self.enabled = False

        joiner_id = interaction.user.id

        try:
            HangmanSession.objects.get(user__id=joiner_id)
        except ObjectDoesNotExist:
            pass
        else:
            await interaction.send(mention_user(joiner_id) + "님, 이미 행맨 게임을 하고 계세요!")
            return

        session = HangmanBattleSession.objects.get(user1__id=self.owner_id)
        session.user2__id = joiner_id  # TODO: would work?

        word_count = EnglishWord.objects.count()
        while True:
            word = EnglishWord.objects.get(pk=randint(1, word_count))
            if len(word.word) >= CommandHangmanBattle.MIN_WORD_LENGTH:
                break
        game = HangmanBattleGame(user1__id=self.owner_id, user2__id=joiner_id, word=word)
        game.start()
        game.save()
        session.game = game
        session.save()


class CommandHangmanBattle(Command):
    """
    [stat] [id or nick]
    행맨 배틀 게임
    행맨 배틀 게임을 시작합니다. stat이 있으면 그 대신 전적을 보여줍니다.
    id 또는 nick이 있으면 해당 유저의 전적을 보여줍니다.
    """

    MIN_WORD_LENGTH = 6
    TOP_RANK_LIMIT = 5

    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "hangmanbattle"

    def get_command_alias(self) -> list:
        return ['hangb', '행맨배틀']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('stat', nargs='?', choices=['stat', 's', '전적', '스탯'], default=None)
        parser.add_argument('nick', nargs='?', default=None)

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        from db_models.hangman.models import HangmanBattleGame, HangmanBattleSession, HangmanSession

        author_id = msg.author.id

        if args.stat:
            return  # TODO

        try:
            HangmanSession.objects.get(user__id=author_id)
        except ObjectDoesNotExist:
            pass
        else:
            await msg.channel.send(mention_user(author_id) + "님, 이미 행맨 게임을 하고 계세요!")
            return

        try:
            session = HangmanBattleSession.objects.get(Q(user1__id=author_id) | Q(user2__id=author_id))
        except ObjectDoesNotExist:
            embed = Embed(color=0x0000FF, title="{}님의 행맨 배틀 방".format(msg.author.display_name), description='대기 중')
            view = JoinView(author_id)
            msg_id = (await msg.channel.send(embed=embed, view=view)).id
            session = HangmanBattleSession(user1_id=author_id, msg_id=msg_id)
            session.save()

            return
        else:
            try:
                session_msg = await msg.channel.fetch_message(session.msg_id)
            except nextcord.errors.NotFound:
                session.msg_id = (await msg.channel.send(session.game.get_msg())).id  # TODO
                session.save()
            else:
                await msg.channel.send(mention_user(author_id) + " 이미 진행 중인 게임이 있어요!", reference=session_msg)
