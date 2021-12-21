# Generated by Django 2.1.15 on 2021-12-22 00:58

from django.db import migrations, models
import django.db.models.deletion

from common import EPermissionLevel
from constants import OWNER_ID


def register_admin(apps, schema_editor):
    User = apps.get_model("common", "User")
    UserPermission = apps.get_model("common", "UserPermission")
    admin_user, _ = User.objects.get_or_create(id=OWNER_ID)
    permission = UserPermission(user=admin_user, level=EPermissionLevel.OWNER)
    permission.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Guild',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GuildPermission',
            fields=[
                ('guild', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='permission', serialize=False, to='common.Guild')),
                ('level', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('role', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='permission', serialize=False, to='common.Role')),
                ('level', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='permission', serialize=False, to='common.User')),
                ('level', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='role',
            name='guild',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guilds', to='common.Guild'),
        ),
        migrations.RunPython(register_admin),
    ]
