import contextlib
import locale

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import database
import infra
import methods
from config import *

with contextlib.suppress(locale.Error):
    locale.setlocale(locale.LC_TIME, "ru_RU")

updater = Updater(token=BOT_TOKEN)
j = updater.job_queue
dispatcher = updater.dispatcher

infra.logging.setup_logger(dispatcher)
infra.storage.setup_database()

dispatcher.add_handler(MessageHandler(Filters.text & Filters.group,
                                      methods.mojno.send_msg))

delta = datetime.time(hour=22, tzinfo=TIMEZONE)

# TODO: Write flexible datetime
j.run_daily(lambda a, b: methods.send_msg(a, b), time=datetime.time(12))

# Specify all methods below
dispatcher.add_handler(CommandHandler('start', methods.on_start))
dispatcher.add_handler(CommandHandler('top', methods.get_top.send_msg))
dispatcher.add_handler(methods.auth.conv_handler)
dispatcher.add_handler(methods.homeworks.conv_handler)
# methods.homeworks.add_handlers(dispatcher)
updater.start_polling()

if LOG_CHAT_ID:
    now = datetime.datetime.now().strftime("%B %d, %H:%M")
    updater.bot.send_message(chat_id=LOG_CHAT_ID,
                             text='Successfully launched!'
                                  ' Current time is:{} \n'
                                  ' Cups of tea: {}'.format(now, CUPS_OF))

updater.idle()

database.db.close()
