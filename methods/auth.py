from enum import Enum, auto

from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext.conversationhandler import ConversationHandler
from telegram.message import Message
from telegram.update import Update

import lyceum_api.login
from database.LyceumUser import LyceumUser
from lyceum_api.parser import Parser, Tag


class States(Enum):
    username = auto()
    password = auto()


def handle_login(bot, update: Update):
    update.message.reply_text('Введите имя пользователя '
                              '(можно без `@lyceum.yaconnect.com`)')
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

    sid, token, resp = lyceum_api.login(username, message.text)

    if sid:
        user, created = LyceumUser.get_or_create(tgid=message.from_user.id)
        user.sid = sid
        user.token = token
        user.username = username
        p = ProfileParser()
        p.feed(resp)
        links = p.get_links()
        if links:
            user.is_teacher = True
            # noinspection PyTypeChecker
            user.course_links = ','.join(links)
        user.save()

        reply = ('Отлично!\n'
                 'Ваш новый sid: {}.'
                 ' Не забудьте его!\n'
                 'Можете начать проверять домашки.'
                 'Введите /hw'.format(sid))
    else:
        reply = 'Неверный логин и/или пароль'

    update.message.reply_text(reply)
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


class ProfileParser(Parser):
    course_links = []
    in_proper_card = False

    def on_feed(self):
        pass

    def on_starttag(self, t: Tag):
        if self.in_proper_card and t.name == 'a':
            self.course_links.append(t.attrs['href'])

    def on_data(self, t: Tag, data: str):
        if t.name == 'h5' and 'card-title' in t.classes and 'Преподаватель' in data:
            self.in_proper_card = True

    def on_endtag(self, t):
        if self.in_proper_card and t.name == 'div' and 'card' in t.classes:
            self.in_proper_card = False

    def get_links(self):
        import re

        return [re.match('.*?([0-9]+)$', x).group(1) for x in self.course_links if x[0] != '#']