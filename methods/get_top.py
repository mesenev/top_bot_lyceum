import random
import re
import pytz
import requests
from config import *

last_update = datetime.datetime.now() - datetime.timedelta(hours=24)

def get_top_without_timecheck(bot, update):
    return get_top(bot, update, True)


def get_top(bot, update, checkpass=False):
    """Prints top of students sorted by their score"""
    global last_update

    time_now = datetime.datetime.now(tz=pytz.timezone('Asia/Vladivostok'))

    if not checkpass and time_now.hour < 6 or time_now.hour > 23:
        bot.send_message(chat_id=update.message.chat_id,
                         text=random.choice(NIGHTTIME_MESSAGES))
        return

    if not checkpass and last_update + COOLDOWN_FOR_LIST > datetime.datetime.now():
        bot.send_message(chat_id=update.message.chat_id,
                         text=random.choice(COOLDOWN_MSGS))
        return

    last_update = datetime.datetime.now()
    message = 'На {} {}:\n'.format(time_now
                                   .strftime("%A, %d %B %Y %I:%M%p"), random.choice(HEADERS))
    kids = sorted(__get_data_from_web(), key=lambda t: t[1], reverse=True)
    i = 0
    j = 0
    while i < (NUMBER_OF_KIDS - 1):
        message += '{}: {} {}\n'.format(TITLES_LIST[j], *kids[i])
        while i + 1 < len(kids) and kids[i][1] == kids[i + 1][1]:
            i += 1
            message += '{}: {} {}\n'.format(TITLES_LIST[j], *kids[i])
        i += 1
        j = j + 1 if j < len(TITLES_LIST) else j

    message += random.choice(AFTERWORDS)

    bot.send_message(chat_id=update.message.chat_id,
                     text=message)
    return


def __get_data_from_web():
    r = requests.get(DATA_URL, cookies={'sessionid': SESSION_ID})
    q = re.search("<table class=(.*?)</table>", r.content.decode().replace('\n','')).group(0)
    kids = [x.replace('&nbsp;', ' ') for x in re.findall('/">(.*?)</a>', q)]
    marks = [float(x) for x in re.findall('(\d*\.\d*)\s*</span>', q)]

    result = []
    for _ in range(0, len(kids)):
        result += [(kids[_], marks[_])]
    return result

