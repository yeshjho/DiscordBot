from db_models.base_model import *


class User(BaseModel):
    id = models.BigIntegerField(primary_key=True)


class Guild(BaseModel):
    id = models.BigIntegerField(primary_key=True)


class Role(BaseModel):
    id = models.BigIntegerField(primary_key=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='guilds')


class UserPermission(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='permission')
    level = models.IntegerField(default=0)


class GuildPermission(BaseModel):
    guild = models.OneToOneField(Guild, on_delete=models.CASCADE, primary_key=True, related_name='permission')
    level = models.IntegerField(default=0)


class RolePermission(BaseModel):
    role = models.OneToOneField(Role, on_delete=models.CASCADE, primary_key=True, related_name='permission')
    level = models.IntegerField(default=0)
