class ECommandExecuteResult:
    SUCCESS = 0
    NO_PERMISSION = 1
    SYNTAX_ERROR = 2
    CUSTOM_ERROR = 3


class EActionExecuteResult:
    NO_MATCH = -1
    SUCCESS = 0
    NO_PERMISSION = 1


class EPermissionLevel:
    BANNED = -1
    DEFAULT = 0
    ADMIN = 10000
    OWNER = 2147483647
