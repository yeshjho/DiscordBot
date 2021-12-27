from actions.action import *

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import nextcord.errors
from nextcord import Message

from helper_functions import *
from .hangman import *


class ActionHangmanBattleGuess(Action):
    async def on_message(self, msg: Message, **kwargs):
        from db_models.hangman.models import HangmanBattleSession, EHangmanBattleState, \
            EHangmanBattleGuessResult, HangmanBattleGame

        if msg.author.bot:
            return EActionExecuteResult.NO_MATCH

        c = msg.content.lower().strip()
        if len(c) != 1 or c not in "abcdefghijklmnopqrstuvwxyz":
            return EActionExecuteResult.NO_MATCH

        author_id = msg.author.id

        try:
            session = HangmanBattleSession.objects.get(Q(user1__id=author_id) | Q(user2__id=author_id))
        except ObjectDoesNotExist:
            return EActionExecuteResult.NO_MATCH

        game: HangmanBattleGame = session.game

        is_first_players_turn = session.state == EHangmanBattleState.FIRST_PLAYER_TURN.value
        if is_first_players_turn and game.user2.id == author_id or \
                session.state == EHangmanBattleState.SECOND_PLAYER_TURN.value and game.user1.id == author_id:
            await msg.channel.send(mention_user(author_id) + "님의 차례가 아닙니다!", delete_after=1)
            return

        if not game:
            return EActionExecuteResult.NO_MATCH

        await msg.delete()

        user1_nick = (await msg.guild.fetch_member(session.game.user1.id)).display_name
        user2_nick = (await msg.guild.fetch_member(session.game.user2.id)).display_name

        guess_result = game.guess(c, author_id == game.user1.id)
        if guess_result == EHangmanBattleGuessResult.WRONG:
            session.state = EHangmanBattleState.FIRST_PLAYER_TURN.value if not is_first_players_turn else \
                EHangmanBattleState.SECOND_PLAYER_TURN
            if is_first_players_turn:
                session.user1_wrong_count += 1
            else:
                session.user2_wrong_count += 1
            session.save()

        elif guess_result == EHangmanBattleGuessResult.ALREADY_USED:
            await msg.channel.send(mention_user(author_id) + " 이미 사용된 글자입니다!", delete_after=1)

        elif guess_result == EHangmanBattleGuessResult.LOSE:
            if is_first_players_turn:
                session.user1_wrong_count += 1
            else:
                session.user2_wrong_count += 1

            if session.user1_wrong_count != session.user2_wrong_count:
                result = HangmanBattleGame.EResult.PLAYER_2_WIN \
                    if session.user1_wrong_count > session.user2_wrong_count else HangmanBattleGame.EResult.PLAYER_1_WIN
                session.finish(result)
                await self.send_result_msg(user1_nick, user2_nick, msg.channel, session, result)
            else:
                session.state = EHangmanBattleState.TIE_BREAKER
            session.save()

        elif guess_result == EHangmanBattleGuessResult.WIN:
            result = HangmanBattleGame.EResult.PLAYER_1_WIN \
                if is_first_players_turn else HangmanBattleGame.EResult.PLAYER_2_WIN
            session.finish(result)
            await self.send_result_msg(user1_nick, user2_nick, msg.channel, session, result)

        user1_nick = (await msg.guild.fetch_member(game.user1.id)).display_name
        user2_nick = (await msg.guild.fetch_member(game.user2.id)).display_name
        txt, embed, view = game.get_msg(user1_nick, user2_nick, EHangmanBattleState(session.state))
        try:
            game_msg = await msg.channel.fetch_message(session.msg_id)
        except nextcord.errors.NotFound:
            msg_id = (await msg.channel.send(txt, embed=embed, view=view)).id
            session.msg_id = msg_id
            session.save()
        else:
            await game_msg.edit(content=txt, embed=embed, view=view)

        return author_id, "guessed letter", c, "in battle"

    @staticmethod
    async def send_result_msg(user1_nick: str, user2_nick: str, channel, session, result):
        from db_models.hangman.models import HangmanBattleGame

        embed = Embed(title="{}님과 {}님의 행맨 결과".format(user1_nick, user2_nick))
        embed.set_image(url=FORCE_FULL_WIDTH_IMAGE_URL)

        if result == HangmanBattleGame.EResult.PLAYER_1_WIN:
            embed.add_field(name=emojify('medal') + ' 승리', value=mention_user(session.game.user1.id))
            embed.add_field(name=emojify('head_bandage') + ' 패배', value=mention_user(session.game.user2.id))
        elif result == HangmanBattleGame.EResult.PLAYER_2_WIN:
            embed.add_field(name=emojify('medal') + ' 승리', value=mention_user(session.game.user2.id))
            embed.add_field(name=emojify('head_bandage') + ' 패배', value=mention_user(session.game.user1.id))
        else:
            embed.add_field(name=emojify('shrug') + ' 무승부', value=EMPTY_LETTER)

        dict_link, meaning = get_meaning(session.game.word.word)
        embed.add_field(name=meaning, value=dict_link, inline=False)
        await channel.send(embed=embed)
