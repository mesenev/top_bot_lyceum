from peewee import CharField, DateField, BooleanField, ForeignKeyField

from database.LyceumGroup import LyceumGroup
from database.database import BotModel


class Student(BotModel):
    fullname = CharField()
    telegram_id = CharField()
    approved = BooleanField(default=False)
    lyceum_group = ForeignKeyField(LyceumGroup)


def update_or_create_user(telegram_id, **kwargs):
    student, is_created = Student.get_or_create(telegram_id=telegram_id)
    student.telegram_id = telegram_id  # TODO: check if set it manually necessary
    for key, val in kwargs.items():
        setattr(student, key, val)
    student.save()
    return student, is_created
