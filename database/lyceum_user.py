from peewee import CharField, IntegerField

from .database import BotModel


class LyceumUser(BotModel):
    tgid = IntegerField(verbose_name='Telegram id', primary_key=True)
    username = CharField(null=True)
    sid = CharField(null=True)
    token = CharField(null=True)
    # never store passwords!
