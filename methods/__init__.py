from telegram.ext import CommandHandler, MessageHandler, Filters

from . import auth
from . import get_top
from . import greeting
from . import homeworks
from . import mojno

METHODS = [
    CommandHandler('start', greeting.on_start),
    MessageHandler(Filters.text & Filters.group, mojno.send_msg),
    CommandHandler('top', get_top.send_msg),
    auth.conv_handler,
    homeworks.conv_handler
]
