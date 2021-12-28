import os

OWNER_ID = 353886187879923712
INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=622425177103269899&permissions=8&scope=bot"
COMMAND_PREFIX = '`'
VERSION = '2.0.3'
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
- 커스텀 커맨드? 길드별로, 권한 레벨 따라 사용할 수 있는 요소 더 많아짐
- 사용자별로 command prefix 설정 가능하게
- 타이머
"""
