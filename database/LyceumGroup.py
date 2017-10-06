from peewee import CharField, DateField, BooleanField

from database.database import BotModel


class LyceumGroup(BotModel):
    alias = CharField()
    telegram_chat_id = CharField()
    lecturer_telegram_id = CharField()
    lecturer_fullname = CharField()
    city = CharField()
    tasks_list_url = CharField()
