from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    permission = models.IntegerField(default=0)


class Message(models.Model):
    id = models.IntegerField(primary_key=True)
