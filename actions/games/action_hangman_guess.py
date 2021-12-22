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

        dict_link = 'http://endic.naver.com/search.nhn?query={}'.format(game.word)
        soup = BeautifulSoup(requests.get(dict_link).content, "lxml")
        try:
            meaning = soup.find('dl', {'class': 'list_e2'}).find('dd').find('span', {'class': 'fnt_k05'}).get_text()
        except AttributeError:
            meaning = ''

        if guess_result == EGuessResult.NORMAL:
            return author_id, "guessed letter", c

        elif guess_result == EGuessResult.LOSE:
            await msg.channel.send("{} 안타깝네요! 정답은 `{}`였습니다!\n{}\n{}".format(
                mention_user(msg.author), game.word, meaning, dict_link))
            session.finish()
            return author_id, "lost"

        elif guess_result == EGuessResult.WIN:
            await msg.channel.send("{} 축하드립니다! 정답을 맞히셨습니다!\n{}\n{}".format(
                mention_user(msg.author), meaning, dict_link))
            session.finish()
            return author_id, "won"
