import pickle
from os.path import isfile
from sys import maxsize

from discord import Member, User, Guild, Role

from constants import *


class EPermissionLevel:
    BANNED = -1
    ALL = 0

    ADMIN = 10000

    OWNER = maxsize


class Permissions:
    def __init__(self):
        self.permission_file_name = "permissions.pickle"

        self.permissions = {'user': {OWNER_ID: EPermissionLevel.OWNER}, 'role': {}, 'guild': {}}

        if isfile(self.permission_file_name):
            with open(self.permission_file_name, "rb") as permission_file:
                self.permissions = pickle.load(permission_file)

    def get_permission_level(self, target: Member or User or Guild or Role or int or str, id_: int = 0) -> int:
        type_ = type(target)

        levels = []

        if type_ is int:
            levels.append(self.permissions['user'].get(target, EPermissionLevel.ALL))
        elif type_ is Member:
            levels.append(self.permissions['user'].get(target.id, EPermissionLevel.ALL))
            levels += [self.permissions['role'].get(role.id, EPermissionLevel.ALL) for role in target.roles]
            levels.append(self.permissions['guild'].get(target.guild.id, EPermissionLevel.ALL))
        elif type_ is User:
            levels.append(self.permissions['user_id'].get(target.id, EPermissionLevel.ALL))
        elif type_ is Guild:
            levels.append(self.permissions['guild'].get(target.guild.id, EPermissionLevel.ALL))
        elif type_ is Role:
            levels.append(self.permissions['role'].get(target.id, EPermissionLevel.ALL))
        elif type_ is str:
            levels.append(self.permissions[target].get(id_, EPermissionLevel.ALL))
        else:
            raise

        min_level = min(levels)
        max_level = max(levels)

        return EPermissionLevel.OWNER if EPermissionLevel.OWNER in levels else \
            (min_level if min_level < EPermissionLevel.ALL else max_level)

    def set_permission_level(self, target: str, id_: int, level: int):
        if target == 'user':
            self.permissions['user'][id_] = level
        elif target == 'guild':
            self.permissions['guild'][id_] = level
        elif target == 'role':
            self.permissions['role'][id_] = level
        else:
            raise

        with open(self.permission_file_name, 'wb') as permission_file:
            pickle.dump(self.permissions, permission_file)


permissions = Permissions()
