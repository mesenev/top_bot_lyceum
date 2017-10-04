import random
import re
import datetime
import requests

from config import SESSION_ID, CUPS_OF
from config_default import NUMBER_OF_KIDS, TIMEZONE, CONTRIBUTORS, COOLDOWN_FOR_LIST, DATA_URL
last_update = datetime.datetime.now() - datetime.timedelta(hours=24)


def _current_time():
    return datetime.datetime.now(tz=TIMEZONE)


def _get_top(bot, update, **kwargs):
    global last_update
    local_time = _current_time()
    checkpass = kwargs['checkpass'] if 'checkpass' in kwargs else False
    if update.message.from_user.id in CONTRIBUTORS:
        checkpass = True
    if not checkpass and local_time.hour < 6 or local_time.hour > 23:
        answ = random.choice(NIGHTTIME_MESSAGES)
        return answ

    if not checkpass and last_update + COOLDOWN_FOR_LIST > datetime.datetime.now():
        answ = random.choice(COOLDOWN_MSGS)
        return answ

    bot.send_message(chat_id=update.message.chat_id, text=random.choice(PREPARE_MESSAGE))
    if update.message.from_user.id not in CONTRIBUTORS:
        last_update = datetime.datetime.now()
    kids = _get_data_from_web()
    answ = _create_top(kids)
    return answ


def send_msg(bot, update, **kwargs):
    message = _get_top(bot, update, **kwargs)
    bot.send_message(chat_id=update.message.chat_id, text=message)


def _create_top(kids_list):
    kids = sorted(kids_list, key=lambda t: t[1], reverse=True)
    i = 0
    j = 0
    message = '{} {}:\n'.format(_current_time().strftime("%B %d, %H:%M"), random.choice(HEADERS))
    while i < NUMBER_OF_KIDS:
        message += '{}: {} {}\n'.format(TITLES_LIST[j], *kids[i])
        while i + 1 < len(kids) and kids[i][1] == kids[i + 1][1]:
            i += 1
            message += '{}: {} {}\n'.format(TITLES_LIST[j], *kids[i])
        i += 1
        j = j + 1 if j < len(TITLES_LIST) else j
    message += random.choice(AFTERWORDS)
    return message


def _get_data_from_web():
    r = requests.get(DATA_URL, cookies={'sessionid': SESSION_ID})
    q = re.search("<table class=(.*?)</table>", r.content.decode().replace('\n', '')).group(0)
    kids = [x.replace('&nbsp;', ' ') for x in re.findall('/">(.*?)</a>', q)]
    marks = [float(x) for x in re.findall('(\d*\.\d*)\s*</span>', q)]

    result = []
    for _ in range(0, len(kids)):
        result += [(kids[_], marks[_])]
    return result


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
PREPARE_MESSAGE = [
    "Давайте позвоним в яндекс",
    "Сейчас узнаем"
]
