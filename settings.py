# for django orm
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'discord',
        'HOST': 'discord-bot.database.windows.net',
        'USER': 'yeshjho@discord-bot',
        'PASSWORD': os.getenv('DISCORD_BOT_DJANGO_PASSWORD'),

        'OPTIONS': {
            'driver': os.getenv('DISCORD_BOT_DB_DRIVER'),
            'unicode_results': True,
            'connection_timeout': 60,
            'query_timeout': 60
        }
    }
}

INSTALLED_APPS = (
    'db_models.common',
    'db_models.hangman',
    'db_models.words',
    'db_models.custom_command_action'
)

SECRET_KEY = os.getenv('DISCORD_BOT_DJANGO_SECRET_KEY')

TIME_ZONE = 'Asia/Seoul'
