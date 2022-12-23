import os

OWNER_ID = 353886187879923712
INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=622425177103269899&permissions=8&scope=bot"
COMMAND_PREFIX = '`'
VERSION = '2.3.2'
TEXT_LENGTH_LIMIT = 2000
IS_TESTING = os.getenv('DISCORD_BOT_IS_TESTING', 'False') == 'True'
PUBLISH_GUILD_ID = 854748691181076490
PUBLISH_CHANNEL_ID = 854749268118994975
RESET_CACHE_EMOJIS = False
FORCE_FULL_WIDTH_IMAGE_URL = 'https://i.imgur.com/Yj6Wsqp.png'
EMPTY_LETTER = '\u200b'


""" TODOS
- slash command - https://discord.com/developers/docs/interactions/slash-commands
- command word
- RPG: 서버를 아예 하나 파서 역할로 "마법사", "도적" 이런 거 해놓고 역할 부여. 각 장소는 채널로 표현
- 사용자별로 command prefix 설정 가능하게
- 타이머

권한 추가 (맨 마지막에 받는 식으로?)
액션마다 권한 추가
"""
