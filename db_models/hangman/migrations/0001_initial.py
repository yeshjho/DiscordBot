# Generated by Django 2.1.15 on 2021-12-23 02:26

import db_models.hangman.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
        ('words', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HangmanGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)])),
                ('guesses', models.CharField(default='', max_length=26, validators=[db_models.hangman.models.validate_lower_case])),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HangmanSession',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='hangman_session', serialize=False, to='common.User')),
                ('msg_id', models.BigIntegerField()),
                ('last_interaction_timestamp', models.DateTimeField(auto_now=True)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='hangman_session', to='hangman.HangmanGame')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='hangmangame',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hangman_games', to='common.User'),
        ),
        migrations.AddField(
            model_name='hangmangame',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hangman_games', to='words.EnglishWord'),
        ),
    ]
