from enum import Enum, auto

from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext.conversationhandler import ConversationHandler
from telegram.message import Message
from telegram.update import Update

import lyceum_api.login
from database.lyceum_user import LyceumUser


class States(Enum):
    username = auto()
    password = auto()


def handle_login(bot, update: Update):
    update.message.reply_text('Введите имя пользователя '
                              '(можно без `@blabla`)')
    return States.username


def handle_username(bot, update: Update, user_data):
    user_data['username'] = update.message.text
    update.message.reply_text('Введите пароль')
    return States.password


def handle_password(bot, update, user_data):
    message: Message = update.message
    username = user_data['username']
    if '@' not in username:
        username += '@lyceum.yaconnect.com'

    sid = lyceum_api.login(username, message.text)

    user, created = LyceumUser.get_or_create(username=username, sid=sid)
    user.tgid = message.from_user.id
    user.save()

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


def get_user(message: Message) -> LyceumUser:
    q = LyceumUser.filter(tgid=message.from_user.id)
    return q[0] if q else None
