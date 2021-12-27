from actions.action import *

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import nextcord.errors
from nextcord import Message
import requests
from bs4 import BeautifulSoup

from helper_functions import *


class ActionHangmanBattleGuess(Action):
    async def on_message(self, msg: Message, **kwargs):
        from db_models.hangman.models import HangmanBattleSession, HangmanGame

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

        game: HangmanGame = session.game
        if not game:
            return EActionExecuteResult.NO_MATCH

        await msg.delete()

        guess_result = game.guess(c)
