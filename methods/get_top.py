import random

from collections import defaultdict
from telegram import Update, Bot
from config import *
from database import LyceumUser, ActiveTop
from methods.common import get_common_data_from_web
last_update = defaultdict(lambda: datetime.datetime.now() - datetime.timedelta(hours=24))


def _current_time():
    return datetime.datetime.now(tz=TIMEZONE)


# noinspection PyTypeChecker,PyCallByClass
def get_top(bot, update, **kwargs):
    global last_update
    local_time = _current_time()
    chat_entity = ActiveTop.get_or_null(ActiveTop, chat_id=update.message.chat_id)
    if not chat_entity:
        bot.send_message(chat_id=update.message.chat_id, text="Команда /top не активна, "
                                                              "пожалуйтесь преподавателю. :)")
        return
    checkpass = kwargs['checkpass'] if 'checkpass' in kwargs else False
    if update.message.from_user.id in CONTRIBUTORS:
        checkpass = True
    #  TODO: Define local night time for chat (based on lecturer data)
    # if not checkpass and local_time.hour < 6 or local_time.hour > 23:
    #     answ = random.choice(NIGHTTIME_MESSAGES)
    #     return answ

    if not checkpass and last_update[chat_entity.id] + COOLDOWN_FOR_LIST > datetime.datetime.now():
        answ = random.choice(COOLDOWN_MSGS)
        return answ

    bot.send_message(chat_id=update.message.chat_id, text=random.choice(PREPARE_MESSAGE))
    if update.message.from_user.id not in CONTRIBUTORS:
        last_update[chat_entity.id] = datetime.datetime.now()
    kids = get_common_data_from_web(chat_entity)
    if kids == 1:
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка авторизации. Выключаюсь.')
        bot.send_message(chat_id=chat_entity.tutor.tgid, text='Ошибка авторизации в чате %s'
                                                              % update.message.chat.title)
        chat_entity.delete_instance()
        return
    answ = _create_top(kids)
    bot.send_message(chat_id=update.message.chat_id, text=answ)


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


# noinspection PyTypeChecker,PyCallByClass
def top_activate(bot: Bot, update: Update, *args):
    author: LyceumUser = LyceumUser.get_or_null(LyceumUser, tgid=update.message.from_user.id)
    chat_entity = ActiveTop.get_or_null(ActiveTop, chat_id=update.message.chat_id)
    if chat_entity:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Бот уже активирован. Чего вы ждали? 🤔🤔 ')
        return
    if not author:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Вы должны быть авторизованы, прошу прощения.')
        return
    if not author.is_teacher:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Разумеется, вы должны быть преподавателем для этого. 🤔')
    links = author.course_links.split(',')
    if len(links) > 1:
        if not args or len(args) > 0 and args[0] not in links:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Уточните группу: варианты {}'.format(" ".join(links)))
            return
        if args[0] in links:
            links = [args[0]]
    chat_entity = ActiveTop.create(chat_id=update.message.chat_id,
                                   tutor=author, token=author.sid, url=DATA_URL.format(links[0]))
    chat_entity.save()
    bot.send_message(chat_id=update.message.chat_id, text='Успешно активировано! Проверьте '
                                                          'командой /top')


# noinspection PyCallByClass,PyTypeChecker
def top_deactivate(bot: Bot, update: Update):
    a = ActiveTop.get_or_null(ActiveTop, chat_id=update.message.chat_id)
    if not a:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Здесь бот не запущен, чего вы ждали? 🤔')
    else:
        a.delete_instance()
        bot.send_message(chat_id=update.message.chat_id,
                         text='Больше не работает!')
