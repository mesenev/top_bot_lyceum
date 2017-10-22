from enum import Enum, auto

from peewee import IntegerField

from .database import BotModel


class Setting(Enum):
    def __new__(cls, value, **kwargs):
        setting_id = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._setting_id_ = setting_id
        obj._value_ = value
        return obj

    class CodeFormat(Enum):
        svg = auto()
        img = auto()
        default = img


class UserSettings(BotModel):
    tgid = IntegerField(verbose_name='Telegram id')
    setting = IntegerField()
    value = IntegerField()

    @staticmethod
    def get(telegram_id: int, setting: Setting):
        res = (UserSettings
               .select()
               .where((UserSettings.tgid == telegram_id)
                      & UserSettings.setting == setting.setting_id)
               .first())
        if res:
            return res.value
        else:
            return setting.default.value
