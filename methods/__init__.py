from telegram.ext import CommandHandler, MessageHandler, Filters

from . import (start, auth, debug,
               get_top, homeworks, mojno,
               style, group_summary, cites)

METHODS = [
    CommandHandler('start', start.on_start),
    CommandHandler('raise', debug.on_raise),
    MessageHandler(Filters.text & Filters.group, mojno.send_msg),
    CommandHandler('top', get_top.get_top),
    CommandHandler('top-activate', get_top.top_activate),
    CommandHandler('top-deactivate', get_top.top_deactivate),
    CommandHandler('summary', group_summary.get_summary),
    CommandHandler('answers', cites.answers),
    auth.conv_handler,
    homeworks.conv_handler,
    style.conv_handler
]
