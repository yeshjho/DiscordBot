# Generated by Django 2.1.15 on 2021-12-22 00:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('words', '0001_initial'),
        ('common', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='HangmanGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.SmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)])),
                ('guesses', models.CharField(max_length=26)),
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
                ('last_interaction_timestamp', models.DateTimeField(auto_now=True)),
                ('game', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='hangman_session', to='hangman.HangmanGame')),
                ('msg', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='common.Message')),
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
