from peewee import CharField, DateField, BooleanField, ForeignKeyField

from database import LyceumGroup
from database.database import BotModel


class Task(BotModel):
    fullname = CharField()
    telegram_id = CharField()
    approved = BooleanField(default=False)
    lyceum_group = ForeignKeyField(LyceumGroup)
