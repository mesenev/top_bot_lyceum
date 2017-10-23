from telegram.ext import CommandHandler, MessageHandler, Filters

from . import (start, auth, debug,
               get_top, homeworks, mojno,
               style,)

METHODS = [
    CommandHandler('start', start.on_start),
    CommandHandler('raise', debug.on_raise),
    MessageHandler(Filters.text & Filters.group, mojno.send_msg),
    CommandHandler('top', get_top.get_top),
    CommandHandler('top-activate', get_top.top_activate),
    CommandHandler('top-deactivate', get_top.top_deactivate),
    auth.conv_handler,
    homeworks.conv_handler,
    homeworks.test_highlight_handler,
    style.conv_handler
]
