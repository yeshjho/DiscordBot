from commands.command import *

from random import choice

import discord.errors


class EGuessResult:
    ALREADY_USED = 0
    WIN = 1
    LOSE = 2
    NORMAL = 3


class HangmanGame:
    def __init__(self, user_id: int, word: str):
        self.state = 0
        self.user_id = user_id
        self.word = word
        self.used_characters = ''

    def guess(self, c: str) -> EGuessResult:
        if c in self.used_characters:
            return EGuessResult.ALREADY_USED

        self.used_characters += c

        if c not in self.word:
            self.state += 1
            if self.state == len(CommandHangman.HANGMAN_ARTS) - 1:
                return EGuessResult.LOSE
        elif all([w in self.used_characters for w in self.word]):
            return EGuessResult.WIN

        return EGuessResult.NORMAL

    def get_word_state(self) -> str:
        chars = []
        for c in self.word:
            chars.append(c if c in self.used_characters else '_')
        return ' '.join(chars).upper()

    def get_character_state(self) -> str:
        chars = []
        for c in 'abcdefghijklmnopqrstuvwxyz':
            chars.append('**' + c + '**' if c not in self.used_characters else '~~*' + c + '*~~')
        return ' '.join(chars).upper()

    def get_msg(self) -> str:
        return "{}님의 행맨\n```\n{}\n```\n```{}```\n{}".format(
            mention_user(self.user_id), CommandHangman.HANGMAN_ARTS[self.state],
            self.get_word_state(), self.get_character_state())


class CommandHangman(Command):
    """
    [stat]
    행맨 게임
    행맨 게임을 시작합니다. stat이 있으면 그 대신 전적을 보여줍니다.
    """

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

    def __init__(self):
        super().__init__()

        self.stat_file_name = "database/hangman_stats.pickle"
        self.session_file_name = "database/hangman_sessions.pickle"

        with open('database/hangman_words.txt') as word_file:
            self.words = [word.strip() for word in word_file.readlines()]

        self.sessions = load_data(self.session_file_name, {})  # user id : [msg id, game]
        self.stats = load_data(self.stat_file_name, {})  # user id : [win_count, lose_count]

        self.MIN_WORD_LENGTH = 3

    def get_command_str(self) -> str:
        return "hangman"

    def get_command_alias(self) -> list:
        return ['hang', '행맨']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('stat', nargs='?', choices=['stat', 's', '전적', '스탯'], default=None)

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        author_id = msg.author.id

        if args.stat:
            win_count, lose_count = self.stats.get(author_id, [0, 0])
            await msg.channel.send("{}님의 행맨 전적: {}승 {}패 (승률 {}%)".format(
                mention_user(msg.author), win_count, lose_count,
                0 if win_count + lose_count == 0 else win_count / (win_count + lose_count) * 100))

            return

        if author_id in self.sessions:
            msg_id, session = self.sessions[author_id]
            try:
                session_msg = await msg.channel.fetch_message(msg_id)
            except discord.errors.NotFound:
                self.sessions[author_id][0] = (await msg.channel.send(self.sessions[author_id][1].get_msg())).id
                save_data(self.session_file_name, self.sessions)
            else:
                await msg.channel.send(mention_user(author_id) + " 이미 진행 중인 게임이 있어요!", reference=session_msg)
        else:
            word = choice(self.words)
            while len(word) < self.MIN_WORD_LENGTH:
                word = choice(self.words)
            self.sessions[author_id] = [-1, HangmanGame(author_id, word)]
            self.sessions[author_id][0] = (await msg.channel.send(self.sessions[author_id][1].get_msg())).id

            save_data(self.session_file_name, self.sessions)

    def get_session(self, user_id: int):
        return self.sessions.get(user_id, [None, None])

    def update_session(self, user_id: int, session):
        self.sessions[user_id] = session
        save_data(self.session_file_name, self.sessions)

    def finish_game(self, user_id: int, won: bool):
        del self.sessions[user_id]
        stats = self.stats.get(user_id, [0, 0])
        if won:
            stats[0] += 1
        else:
            stats[1] += 1
        self.stats[user_id] = stats

        save_data(self.session_file_name, self.sessions)
        save_data(self.stat_file_name, self.stats)
