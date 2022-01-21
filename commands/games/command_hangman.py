from commands.command import *

from random import randint

import nextcord.errors
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from helper_functions import *


class CommandHangman(Command):
    """
    [stat] [id or nick]
    행맨 게임
    행맨 게임을 시작합니다. stat이 있으면 그 대신 전적을 보여줍니다.
    id 또는 nick이 있으면 해당 유저의 전적을 보여줍니다.
    """

    MIN_WORD_LENGTH = 4
    TOP_RANK_LIMIT = 5

    def __init__(self):
        super().__init__()

    def get_command_str(self) -> str:
        return "hangman"

    def get_command_alias(self) -> list:
        return ['hang', '행맨']

    def fill_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('stat', nargs='?', choices=['stat', 's', '전적', '스탯'], default=None)
        parser.add_argument('nick', nargs='?', default=None)

    @execute_condition_checker()
    async def execute(self, msg: Message, args: argparse.Namespace, **kwargs):
        from db_models.hangman.models import HangmanGame, HangmanSession, HangmanBattleSession, HANGMAN_PARTS
        from db_models.words.models import EnglishWord

        if args.nick:
            if args.permission_level < 1:
                return ECommandExecuteResult.NO_PERMISSION
            else:
                try:
                    target_user_id = await get_user_id(args.nick, msg.guild)
                except MultipleUserException:
                    raise CommandExecuteError("해당하는 유저가 없거나 여러 명입니다!", delete_after=2)
        else:
            target_user_id = msg.author.id

        user = await msg.guild.fetch_member(target_user_id)

        if args.stat:
            games = HangmanGame.objects.filter(hangman_session=None, user__id=user.id)
            total_count = games.count()
            if total_count == 0:
                await msg.channel.send(user.display_name + "님은 아직 플레이한 적이 없습니다.")
                return

            lose_count = games.filter(state=HANGMAN_PARTS).count()
            win_count = total_count - lose_count
            perfect_count = games.filter(state=0).count()
            almost_lost_count = games.filter(state=5).count()

            win_rate = win_count / total_count * 100
            perfect_rate = perfect_count / win_count * 100 if win_count else 0
            almost_lost_rate = almost_lost_count / win_count * 100 if win_count else 0

            times_used = {}
            right_count = {}
            wrong_count = {}
            close_count = 0
            for game in games:
                if game.state == HANGMAN_PARTS and len(set(game.word.word) - set(game.guesses)) == 1:
                    close_count += 1
                for c in game.guesses:
                    times_used[c] = times_used.get(c, 0) + 1
                    count_to_add = right_count if c in game.word.word else wrong_count
                    count_to_add[c] = count_to_add.get(c, 0) + 1

            right_count = sorted(right_count.items(), key=lambda e: e[1] / times_used[e[0]],
                                 reverse=True)[:CommandHangman.TOP_RANK_LIMIT]
            wrong_count = sorted(wrong_count.items(), key=lambda e: e[1] / times_used[e[0]],
                                 reverse=True)[:CommandHangman.TOP_RANK_LIMIT]
            times_used_top = sorted(times_used.items(), key=lambda e: e[1],
                                    reverse=True)[:CommandHangman.TOP_RANK_LIMIT]

            close_rate = close_count / lose_count * 100 if lose_count else 0

            average_state = sum([game.state % HANGMAN_PARTS for game in games]) / win_count \
                if win_count else ''
            average_word_length = sum([len(game.word.word) for game in games]) / total_count

            embed = get_embed("{}님의 행맨 전적".format(user.display_name))
            embed.colour = round((100 - win_rate) / 100 * 255) * 16 ** 4 + round(win_rate / 100 * 255)
            embed.set_image(url=FORCE_FULL_WIDTH_IMAGE_URL)

            embed.add_field(name="{}승 {}패".format(win_count, lose_count), value="승률 `{:.2f}%`".format(win_rate))
            embed.add_field(name="승리 시 평균 행맨 진행도", value="`{:.2f}`".format(average_state) if average_state else '-')
            embed.add_field(name='평균 단어 길이', value='`{:.2f}`'.format(average_word_length))

            embed.add_field(name="완승", value="`{}` ({:.2f}%)".format(perfect_count, perfect_rate))
            embed.add_field(name="석패", value="`{}` ({:.2f}%)".format(close_count, close_rate))
            embed.add_field(name="기사회생", value="`{}` ({:.2f}%)".format(almost_lost_count, almost_lost_rate))

            embed.add_field(name='사용률 Top {}'.format(CommandHangman.TOP_RANK_LIMIT),
                            value="\n".join(["`{}`: {}".format(e[0], e[1]) for e in times_used_top]))
            embed.add_field(name='정답률 Top {}'.format(CommandHangman.TOP_RANK_LIMIT),
                            value="\n".join(["`{}`: {:.2f}% ({}/{})".format(e[0], e[1] / times_used[e[0]] * 100, e[1],
                                                                            times_used[e[0]]) for e in right_count]))
            embed.add_field(name='오답률 Top {}'.format(CommandHangman.TOP_RANK_LIMIT),
                            value="\n".join(["`{}`: {:.2f}% ({}/{})".format(e[0], e[1] / times_used[e[0]] * 100, e[1],
                                                                            times_used[e[0]]) for e in wrong_count]))
            await msg.channel.send(embed=embed)

            return

        author_id = msg.author.id

        try:
            HangmanBattleSession.objects.get(Q(user1__id=author_id) | Q(user2__id=author_id))
        except ObjectDoesNotExist:
            pass
        else:
            await msg.channel.send(mention_user(author_id) + "님, 이미 행맨 배틀 게임을 하고 계세요!")
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
