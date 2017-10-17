from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import infra
import methods
from config import *

updater = Updater(token=BOT_TOKEN)
j = updater.job_queue
dispatcher = updater.dispatcher

infra.logging.setup_logger(dispatcher)
infra.storage.setup_database()
infra.i18n.setup_locale()

# TODO: Write flexible datetime
j.run_daily(lambda a, b: methods.send_msg(a, b), time=datetime.time(12))

# Specify all methods below
dispatcher.add_handler(CommandHandler('start.py', methods.on_start))
dispatcher.add_handler(CommandHandler('top', methods.get_top.send_msg))
dispatcher.add_handler(CommandHandler('top-activate', methods.get_top.top_activate))
dispatcher.add_handler(methods.auth.conv_handler)
dispatcher.add_handler(methods.homeworks.conv_handler)
dispatcher.add_handler(MessageHandler(Filters.text & Filters.group,  # useless chatting
                                      methods.mojno.send_msg))
# methods.homeworks.add_handlers(dispatcher)
updater.start_polling()

if LOG_CHAT_ID:
    now = datetime.datetime.now().strftime("%B %d, %H:%M")
    updater.bot.send_message(chat_id=LOG_CHAT_ID,
                             text='Successfully launched!'
                                  ' Current time is:{} \n'
                                  ' Cups of tea: {}'.format(now, CUPS_OF))

updater.idle()

infra.storage.db.close()
