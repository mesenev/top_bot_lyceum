import locale

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import database
import methods
from config import *

database.db.connect()
database.db.create_tables(database.models, safe=True)

try:
    locale.setlocale(locale.LC_TIME, "ru_RU")
except:
    pass

updater = Updater(token=BOT_TOKEN)
j = updater.job_queue
dispatcher = updater.dispatcher

setup_logger(dispatcher)

dispatcher.add_handler(MessageHandler(Filters.text & Filters.group,
                                      methods.mojno.send_msg))

delta = datetime.time(hour=22, tzinfo=TIMEZONE)

# TODO: Write flexible datetime
j.run_daily(lambda a, b: methods.send_msg(a, b), time=datetime.time(12))

# Specify all methods below
dispatcher.add_handler(CommandHandler('top', methods.get_top.send_msg))
dispatcher.add_handler(methods.auth.conv_handler)
dispatcher.add_handler(methods.homeworks.conv_handler)

updater.start_polling()

updater.idle()

database.db.close()