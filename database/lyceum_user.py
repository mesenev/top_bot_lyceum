from peewee import CharField, IntegerField

from .database import BotModel


class LyceumUser(BotModel):
    tgid = IntegerField(verbose_name='Telegram id', primary_key=True)
    sid = CharField()
    username = CharField()
    # never store passwords!
