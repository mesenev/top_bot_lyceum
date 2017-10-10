from enum import Enum, auto

from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext.conversationhandler import ConversationHandler
from telegram.update import Update

import lyceum_api.login


class States(Enum):
    username = auto()
    password = auto()


def handle_login(bot, update: Update):
    update.message.reply_text('Введите имя пользователя '
                              '(можно без @blabla)')
    return States.username


def handle_username(bot, update: Update, user_data):
    user_data['username'] = update.message.text
    update.message.reply_text('Введите пароль')
    return States.password


def handle_password(bot, update, user_data):
    sid = lyceum_api.login(user_data['username'],
                           update.message.text)
    update.message.reply_text('Ваш новый sid: {}.'
                              ' Не забудьте его!'.format(sid))
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('login', handle_login, Filters.private)],

    states={
        States.username: [MessageHandler(Filters.text,
                                         handle_username,
                                         pass_user_data=True)],
        States.password: [MessageHandler(Filters.text,
                                         handle_password,
                                         pass_user_data=True)]
    },
    fallbacks=[]
)
