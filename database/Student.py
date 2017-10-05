from django.db.models import ForeignKey
from peewee import CharField, DateField, BooleanField

from database import LyceumGroup
from database.database import BotModel


class Student(BotModel):
    fullname = CharField()
    telegram_id = CharField()
    city = CharField()
    lyceumgroup_id = ForeignKey(LyceumGroup)


def update_or_create_user(telegramid, **kwargs):
    student, is_created = Student.get_or_create(telegram_id=telegramid)
    student.telegram_id = telegramid  # TODO: check if set it manually necessary
    for key, val in kwargs.items():
        setattr(student, key, val)
    student.save()
    return student, is_created
