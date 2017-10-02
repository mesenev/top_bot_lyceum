from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from parse_grid import get_data
from config import *

import logging
import random
import pytz
import locale

locale.setlocale(locale.LC_TIME, "ru_RU")

updater = Updater(token=BOT_TOKEN)
j = updater.job_queue
dispatcher = updater.dispatcher
last_update = datetime.datetime.now() - datetime.timedelta(hours=24)

# TODO: logging section should be in config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='log')
logger = logging.getLogger(__name__)


# log all errors
def error(bot, update, err):
    logger.warning('Update "%s" caused error "%s"' % (update, err))


dispatcher.add_error_handler(error)


def start(bot, update):
    update.message.reply_text('Привет. Новости с полей.')


def get_top(bot, update):
    global last_update
    time_now = datetime.datetime.now(tz=pytz.timezone('Asia/Vladivostok'))

    if time_now.hour < 6 or time_now.hour > 23:
        logging.INFO()
        bot.send_message(chat_id=update.message.chat_id,
                         text=random.choice(NIGHTTIME_MESSAGES))
        return

    if last_update + COOLDOWN_FOR_LIST > datetime.datetime.now():
        bot.send_message(chat_id=update.message.chat_id,
                         text=random.choice(COOLDOWN_MSGS))
        return

    last_update = datetime.datetime.now()
    message = 'На {} {}:\n'.format(time_now
                                   .strftime("%A, %d %B %Y %I:%M%p"), random.choice(HEADERS))
    kids = sorted(get_data(), key=lambda t: t[1], reverse=True)
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


def greeting(bot, update):
    input = ''.join(filter(str.isalpha, update.message.text.lower()))
    if input == 'приветбот':
        if update.message.from_user.id in CONTRIBUTORS:
            bot.send_message(chat_id=update.message.chat_id, text=random.choice(GREETING_TO_CONTRIBUTOR))
            return
    bot.send_message(chat_id=update.message.chat_id, text=random.choice(GREETING_TO_SOMEONE)
                     .format(name=update.message.from_user.first_name))
    return


echo_handler = MessageHandler(Filters.text, greeting)
dispatcher.add_handler(echo_handler)


job_minute = j.run_daily(get_top, time=datetime.time(22))

updater.dispatcher.add_handler(CommandHandler('top', get_top))
updater.dispatcher.add_handler(CommandHandler('start', start))

updater.start_polling()

updater.idle()
