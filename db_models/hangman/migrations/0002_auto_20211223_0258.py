# Generated by Django 2.1.15 on 2021-12-23 02:58

from django.db import migrations

import datetime
import re
from glob import glob


lost_letters = {
    'overdosing': 'abcdeilnopst',
    'smidgins': 'aeghiknpst',
    'width': 'aeilnsty',
    'tinkle': 'acdegilnpst',
    'tribulation': 'acefhinoprstu',
    'bronzes': 'adefgij',
    'dialyses': 'acdefgimost',
    'tomcat': 'adegirs',
    'jailbreak': 'adefhilnrst',
    'pairs': 'abcdefor',
    'feting': 'begilnprstw',
    'explicated': 'adehiklnostu',
    'suffragans': 'abcdeiorsu',
    'lintels': 'aceilmnouy',
    'purify': 'aeinostu',
    'exporters': 'aefilmnorst',
    'rummage': 'aegilnostu',
    'clad': 'aeiostu',
    'easing': 'aefgilmnprt',
    'banns': 'aehiouy',
    'placenta': 'adeinopst',
    'evils': 'adeinopst',
    'cavalcade': 'acdeimnrst',
    'youngish': 'acdeiorstu',
    'ridged': 'aeimnost',
    'nonchalantly': 'adeghinopst',
    'engorged': 'aeilnopst',
    'revamped': 'adeilmnoprst',
    'fetlocks': 'aeghinostu',
    'promiscuity': 'aehiklnoprstuy',
    'movables': 'acdeilnorst',
    'mazurkas': 'aceilnosu',
    'towpath': 'aeilnosty',
    'aurae': 'cdenrstw',
    'coalesces': 'adeilnpsty',
    'yanked': 'acdeghnrst',
    'flask': 'aehlmpsty',
    'scalars': 'aeinoprst',
    'scandalizes': 'aceiklmnpstvx',
    'mayflower': 'acdeinorst',
    'nosing': 'aceloru',
    'infertility': 'acefilnopstvy',
    'epoch': 'aeinrst',
    'swan': 'aehilosu',
}


def migrate_from_log(apps, schema_editor):
    HangmanGame = apps.get_model("hangman", "HangmanGame")
    User = apps.get_model("common", "User")
    EnglishWord = apps.get_model("words", "EnglishWord")

    start_pat = r'\[(.+)\] Command hangman: used by .+ \((\d+)\).+word = (\w+)'
    guess_pat = r'Hangman: (\d+) guessed letter (\w)'
    finish_pat = r'Hangman: (\d+) (won|lost)'

    games = {}
    timestamps = {}

    log_files = glob('logs/*.txt')
    log_files.reverse()
    for log in log_files:
        with open(log, encoding='utf-8') as f:
            for line in f.readlines():
                if result := re.search(start_pat, line):
                    timestamp = datetime.datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S.%f')
                    user_id = result[2]
                    word = result[3]
                    user, _ = User.objects.get_or_create(id=int(user_id))
                    english_word = EnglishWord.objects.get(word=word)
                    games[user_id] = HangmanGame(user=user, word=english_word)
                    timestamps[user_id] = timestamp
                elif result := re.search(guess_pat, line):
                    user_id = result[1]
                    letter = result[2]
                    games[user_id].guesses += letter
                elif result := re.search(finish_pat, line):
                    user_id = result[1]
                    has_won = result[2] == 'won'
                    game = games[user_id]
                    if has_won:
                        for guess in game.guesses:
                            if guess not in game.word.word:
                                game.state += 1
                        for letter in game.word.word:
                            if letter not in game.guesses:
                                game.guesses += letter
                    else:
                        game.state = 6
                        actual_used = lost_letters[game.word.word]
                        for c in actual_used:
                            if c not in game.guesses:
                                game.guesses += c
                                break
                        else:
                            raise

                    game.save()
                    HangmanGame.objects.filter(pk=game.pk).update(timestamp=timestamps[user_id])
                    del games[user_id]
                    del timestamps[user_id]


class Migration(migrations.Migration):

    dependencies = [
        ('hangman', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_from_log)
    ]