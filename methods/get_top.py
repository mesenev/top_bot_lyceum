import random

from telegram import Update, Bot

from config import *
from database import LyceumUser, ActiveTop
from methods.common import get_common_data_from_web

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
    kids = get_common_data_from_web()
    answ = _create_top(kids)
    return answ


def send_msg(bot, update, **kwargs):
    message = _get_top(bot, update, **kwargs)
    bot.send_message(chat_id=update.message.chat_id, text=message)


def _create_top(kids_list):
    kids = kids_list
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


def top_activate(bot: Bot, update: Update, *args):
    #Кейс если пользователь не авторизован
    author: LyceumUser = LyceumUser.get(tgid=update.message.from_user.id)
    chat_entity = ActiveTop.get(chat_id=update.message.chat_id)
    if not chat_entity:
        bot.send_message(chat_id=update.message.chat_id,
                         message='Бот уже активирован. Чего вы ждали? ')  # TODO: emoji
        return
    if not author:
        bot.send_message(chat_id=update.message.chat_id,
                         message='Вы должны быть авторизованы, прошу прощения.')
        return
    if not author.is_teacher:
        bot.send_message(chat_id=update.message.chat_id,
                         message='Разумеется, вы должны быть преподавателем для этого.')
    links = author.course_links.split(',')
    if len(links) > 1:
        if not args or len(args) > 0 and args[0] not in links:
            bot.send_message(chat_id=update.message.chat_id,
                             message='Уточните группу: варианты {}'.format(" ".join(links)))
            return
        if args[0] in links:
            links = [args[0]]
    chat_entity = ActiveTop.create(chat_id=update.message.chat_id,
                                   tutor=author, token=author.token, link=links[0])
    chat_entity.save()
    #Кейс, если топ уже активирован
    # Кейс, если топ уже активирован

def top_deactivate(bot: Bot, update: Update):
    a = ActiveTop.get(update.message.chat_id)
