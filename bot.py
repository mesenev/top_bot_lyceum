import locale
import pytz
import methods
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import *
from methods import get_top, greeting

try:
    locale.setlocale(locale.LC_TIME, "ru_RU")
except:
    pass

updater = Updater(token=BOT_TOKEN)
j = updater.job_queue
dispatcher = updater.dispatcher

setup_logger(dispatcher)

echo_handler = MessageHandler(Filters.text, greeting)
dispatcher.add_handler(echo_handler)

delta = datetime.time(hour=22, tzinfo=pytz.timezone('Asia/Vladivostok'))

# TODO: Write flexible datetime
j.run_daily(methods.get_top_without_timecheck, time=datetime.time(12))


# Specify all methods below
dispatcher.add_handler(CommandHandler('top', methods.get_top))

updater.start_polling()

updater.idle()
