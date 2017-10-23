from peewee import CharField, IntegerField, ForeignKeyField

from .database import BotModel
from .LyceumUser import LyceumUser


class ActiveTop(BotModel):
    chat_id = IntegerField(verbose_name='Telegram chat id', primary_key=True)
    tutor = ForeignKeyField(LyceumUser)
    token = CharField()
    url = CharField()
