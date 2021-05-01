from actions.action import *

import discord.errors
from discord import Message

from commands.games.command_hangman import CommandHangman, EGuessResult
from helper_functions import *


class ActionHangmanGuess(Action):
    async def on_message(self, msg: Message, **kwargs):
        c = msg.content.lower().strip()
        if len(c) != 1 or c not in "abcdefghijklmnopqrstuvwxyz":
            return EActionExecuteResult.NO_MATCH

        hangman_command: CommandHangman = kwargs['commands_map']['hangman']

        author_id = msg.author.id
        msg_id, game = hangman_command.get_session(author_id)
        if game is None:
            return EActionExecuteResult.NO_MATCH

        await msg.delete()

        guess_result = game.guess(c)
        if guess_result == EGuessResult.ALREADY_USED:
            await msg.channel.send(mention_user(msg.author) + " 이미 사용된 글자입니다!", delete_after=1)
        else:
            try:
                game_msg = await msg.channel.fetch_message(msg_id)
            except discord.errors.NotFound:
                msg_id = (await msg.channel.send(game.get_msg())).id
            else:
                await game_msg.edit(content=game.get_msg())

            if guess_result == EGuessResult.NORMAL:
                hangman_command.update_session(author_id, [msg_id, game])

            elif guess_result == EGuessResult.LOSE:
                await msg.channel.send("{} 안타깝네요! 정답은 `{}`였습니다!\n{}".format(
                    mention_user(msg.author), game.word,
                    'https://en.dict.naver.com/#/search?query={}'.format(game.word)))
                hangman_command.finish_game(author_id, False)

            elif guess_result == EGuessResult.WIN:
                await msg.channel.send(mention_user(msg.author) + " 축하드립니다! 정답을 맞히셨습니다!")
                hangman_command.finish_game(author_id, True)

            else:
                raise
