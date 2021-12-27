from commands.command import *

from random import randint

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import nextcord.errors
from nextcord.interactions import Interaction
import nextcord.ui as ui
from nextcord import ButtonStyle

from helper_functions import *


class JoinView(ui.View):
    def __init__(self, owner_id, owner_name):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.enabled = True

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.user.id != self.owner_id and self.enabled

    @ui.button(label='참가', style=ButtonStyle.primary)
    async def join_game(self, button: ui.Button, interaction: Interaction):
        from db_models.common.models import User
        from db_models.hangman.models import HangmanBattleGame, HangmanBattleSession, HangmanSession, \
            EHangmanBattleState
        from db_models.words.models import EnglishWord

        joiner_id = interaction.user.id

        try:
            HangmanSession.objects.get(user__id=joiner_id)
        except ObjectDoesNotExist:
            pass
        else:
            await interaction.send(mention_user(joiner_id) + "님, 이미 행맨 게임을 하고 계세요!")
            return

        session = HangmanBattleSession.objects.get(user1__id=self.owner_id)
        try:
            cur_session = HangmanBattleSession.objects.get(Q(user1__id=joiner_id) | Q(user2__id=joiner_id))
        except ObjectDoesNotExist:
            pass
        else:
            if session.id != cur_session.id:
                await interaction.send(mention_user(joiner_id) + "님, 이미 행맨 배틀 게임을 하고 계세요!")
                return

        if session.user1.id == joiner_id:
            return

        if not self.enabled:
            return
        self.enabled = False

        session.user2 = User.objects.get(id=joiner_id)

        word_count = EnglishWord.objects.count()
        while True:
            word = EnglishWord.objects.get(pk=randint(1, word_count))
            if len(word.word) >= CommandHangmanBattle.MIN_WORD_LENGTH:
                break

        is_first_player_owner = bool(randint(0, 1))

        game = HangmanBattleGame(user1_id=self.owner_id if is_first_player_owner else joiner_id,
                                 user2_id=joiner_id if is_first_player_owner else self.owner_id, word=word)
        game.save()
        session.game = game
        session.save()

        joiner_name = interaction.user.display_name
        msg, embed, view = game.get_msg(self.owner_name if is_first_player_owner else joiner_name,
                                        joiner_name if is_first_player_owner else self.owner_name,
                                        EHangmanBattleState(session.state))
        await interaction.edit(content=msg, embed=embed, view=view)


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
        from db_models.hangman.models import HangmanBattleGame, HangmanBattleSession, \
            HangmanSession, EHangmanBattleState

        if args.nick:
            if args.permission_level < 1:
                return ECommandExecuteResult.NO_PERMISSION
            else:
                try:
                    target_user_id = await get_user_id(args.nick, msg.guild)
                except MultipleUserException:
                    return ECommandExecuteResult.CUSTOM_ERROR, "해당하는 유저가 없거나 여러 명입니다!"
        else:
            target_user_id = msg.author.id

        user = await msg.guild.fetch_member(target_user_id)

        if args.stat:
            games = HangmanBattleGame.objects.filter(hangman_battle_session=None)
            user1_games = games.filter(user1__id=user.id)
            user2_games = games.filter(user2__id=user.id)
            total_count = user1_games.count() + user2_games.count()
            if total_count == 0:
                await msg.channel.send(user.display_name + "님은 아직 플레이한 적이 없습니다.")
                return

            win_count = user1_games.filter(state=HangmanBattleGame.EResult.PLAYER_1_WIN.value).count() + \
                        user2_games.filter(state=HangmanBattleGame.EResult.PLAYER_2_WIN.value).count()
            draw_count = user1_games.filter(state=HangmanBattleGame.EResult.DRAW.value).count() + \
                         user2_games.filter(state=HangmanBattleGame.EResult.DRAW.value).count()
            lose_count = total_count - win_count - draw_count

            return

        author_id = msg.author.id

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
            view = JoinView(author_id, msg.author.display_name)
            msg_id = (await msg.channel.send(embed=embed, view=view)).id
            session = HangmanBattleSession(user1_id=author_id, msg_id=msg_id)
            session.save()
            return

        else:
            try:
                session_msg = await msg.channel.fetch_message(session.msg_id)
            except nextcord.errors.NotFound:
                user1_name = (await msg.guild.fetch_member(session.game.user1.id)).display_name
                user2_name = (await msg.guild.fetch_member(session.game.user2.id)).display_name
                txt, embed, view = session.game.get_msg(user1_name, user2_name, EHangmanBattleState(session.state))
                session.msg_id = (await msg.channel.send(content=txt, embed=embed, view=view)).id
                session.save()
            else:
                await msg.channel.send(mention_user(author_id) + " 이미 진행 중인 배틀 게임이 있어요!", reference=session_msg)
