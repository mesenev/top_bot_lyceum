import infra.logging
infra.logging.setup_logger()  # this should go before anything else

from telegram.ext import Updater

import infra
import methods
from config import *

updater = Updater(token=BOT_TOKEN)
j = updater.job_queue

infra.logging.setup_dispatcher_logging(updater.dispatcher)
infra.storage.setup_database()
infra.i18n.setup_locale()


for handler in methods.METHODS:
    updater.dispatcher.add_handler(handler)

if LOG_CHAT_ID:
    methods.start.send_startup_greeting(updater.bot, LOG_CHAT_ID)

updater.start_polling()
updater.idle()

infra.storage.db.close()
