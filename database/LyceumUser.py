from peewee import CharField, IntegerField, BooleanField
from .database import BotModel


class LyceumUser(BotModel):
    tgid = IntegerField(verbose_name='Telegram id', primary_key=True)
    username = CharField(null=True)
    sid = CharField(null=True)
    token = CharField(null=True)
    is_teacher = BooleanField(default=False)
    course_links = CharField(null=True)
    # never store passwords!
