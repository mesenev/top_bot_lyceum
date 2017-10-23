import datetime

import pytz

CUPS_OF = 28
LOGIN = ''
PASSWORD = ''
LOG_CHAT_ID = ''
NUMBER_OF_KIDS = 5
COOLDOWN_FOR_LIST = datetime.timedelta(hours=3)
TIMEZONE = pytz.timezone('Asia/Vladivostok')


TITLES_LIST = [
    '👑 Бессменный лидер',
    '🥈 Неустанный преследователь',
    '🥉 Один из лучших',
    'Знает, что делает',
    'Хороший парень',
]

AFTERWORDS = [
    'Удачи ❤',
    'Этот список заговорён на удачу',
    'Похоже, кто-то хочет чай ☕',
    'Мои создатели выпили {} кружки чая ☕'.format(CUPS_OF),
]

NIGHTTIME_MESSAGES = [
    'Ночью доставка не работает. Добрых снов, добрый человек. 🚀',
    'Возвращайтесь на рассвете 🚀',
]

HEADERS = [
    'расклады следующие',
    'отметились',
    'зал славы',
]

COOLDOWN_MSGS = [
    'Терпение, друг',
    'Ещё рано',
    'Терпение, терпение',
]
PREPARE_MESSAGE =[
    "Давайте позвоним в Яндекс",
    "Сейчас узнаем"
]

CONTRIBUTORS = [
    102660981,  # mesenev
    82204126,   # malyavin
]
