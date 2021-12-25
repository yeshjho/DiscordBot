from actions.action import *

from django.core.exceptions import ObjectDoesNotExist
import nextcord.errors
from nextcord import Message
import requests
from bs4 import BeautifulSoup

from helper_functions import *


class ActionHangmanGuess(Action):
    async def on_message(self, msg: Message, **kwargs):
        from db_models.hangman.models import HangmanSession, EGuessResult

        if msg.author.bot:
            return EActionExecuteResult.NO_MATCH

        c = msg.content.lower().strip()
        if len(c) != 1 or c not in "abcdefghijklmnopqrstuvwxyz":
            return EActionExecuteResult.NO_MATCH

        author_id = msg.author.id

        try:
            session = HangmanSession.objects.get(user__id=author_id)
        except ObjectDoesNotExist:
            return EActionExecuteResult.NO_MATCH

        await msg.delete()

        game = session.game
        guess_result = game.guess(c)

        if guess_result == EGuessResult.ALREADY_USED:
            await msg.channel.send(mention_user(msg.author) + " 이미 사용된 글자입니다!", delete_after=1)
            return

        try:
            game_msg = await msg.channel.fetch_message(session.msg_id)
        except nextcord.errors.NotFound:
            msg_id = (await msg.channel.send(game.get_msg())).id
            session.msg_id = msg_id
            session.save()
        else:
            await game_msg.edit(content=game.get_msg())

        dict_link = 'http://endic.naver.com/search.nhn?query={}'.format(game.word.word)
        soup = BeautifulSoup(requests.get(dict_link).content, "lxml")
        try:
            meaning = soup.find('dl', {'class': 'list_e2'}).find('dd').find('span', {'class': 'fnt_k05'}).get_text()
        except AttributeError:
            meaning = ''

        if guess_result == EGuessResult.NORMAL:
            return author_id, "guessed letter", c

        embed = Embed(title="{}님의 행맨 결과".format(msg.author.display_name))
        to_return = None
        if guess_result == EGuessResult.LOSE:
            embed.colour = 0xFF0000
            embed.add_field(name='패배', value='안타깝네요! 정답은 `{}`였습니다!'.format(game.word.word))
            to_return = "and lost"
        elif guess_result == EGuessResult.WIN:
            embed.colour = 0x0000FF
            embed.add_field(name='승리', value='축하드립니다! 정답을 맞히셨습니다!')
            to_return = "and won"

        session.finish()
        embed.add_field(name=meaning, value=dict_link, inline=False)
        await msg.channel.send(embed=embed)
        return author_id, "guessed letter", c, to_return
