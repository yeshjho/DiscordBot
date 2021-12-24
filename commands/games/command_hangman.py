from commands.command import *

from random import randint

import nextcord.errors
from django.core.exceptions import ObjectDoesNotExist

from helper_functions import *


class CommandHangman(Command):
    """
    [stat]
    행맨 게임
    행맨 게임을 시작합니다. stat이 있으면 그 대신 전적을 보여줍니다.
    """

    MIN_WORD_LENGTH = 4

    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "hangman"

    def get_command_alias(self) -> list:
        return ['hang', '행맨']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('stat', nargs='?', choices=['stat', 's', '전적', '스탯'], default=None)

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        from db_models.hangman.models import HangmanGame, HangmanSession
        from db_models.words.models import EnglishWord

        author_id = msg.author.id

        if args.stat:
            games = HangmanGame.objects.filter(hangman_session=None, user__id=author_id)
            total_count = games.count()
            lose_count = games.filter(state=HangmanGame.HANGMAN_PARTS).count()
            win_count = total_count - lose_count
            perfect_count = games.filter(state=0).count()
            almost_lost_count = games.filter(state=5).count()
            await msg.channel.send("{}님의 행맨 전적: {}승 {}패 (승률 {:.2f}%)\n완승: {} ({:.2f}%)\n기사회생: {} ({:.2f})"
                .format(
                    mention_user(msg.author), win_count, lose_count,
                    0 if total_count == 0 else win_count / total_count * 100,
                    perfect_count, 0 if total_count == 0 else perfect_count / total_count * 100,
                    almost_lost_count, 0 if total_count == 0 else almost_lost_count / total_count * 100
                )
            )

            return

        try:
            session = HangmanSession.objects.get(user__id=author_id)
        except ObjectDoesNotExist:
            word_count = EnglishWord.objects.count()
            while True:
                word = EnglishWord.objects.get(pk=randint(1, word_count))
                if len(word.word) >= CommandHangman.MIN_WORD_LENGTH:
                    break
            game = HangmanGame(user_id=author_id, word=word)
            game.save()
            msg_id = (await msg.channel.send(game.get_msg())).id
            session = HangmanSession(user_id=author_id, game=game, msg_id=msg_id)
            session.save()

            return ECommandExecuteResult.SUCCESS, "word =", word.word
        else:
            try:
                session_msg = await msg.channel.fetch_message(session.msg_id)
            except nextcord.errors.NotFound:
                session.msg_id = (await msg.channel.send(session.game.get_msg())).id
                session.save()
            else:
                await msg.channel.send(mention_user(author_id) + " 이미 진행 중인 게임이 있어요!", reference=session_msg)
