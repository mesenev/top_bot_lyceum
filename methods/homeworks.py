from enum import Enum, auto

import requests
from telegram.callbackquery import CallbackQuery
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.dispatcher import Dispatcher
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.parsemode import ParseMode
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.update import Update

from database.lyceum_user import LyceumUser
from lyceum_api import get_check_queue
from lyceum_api.issue import QueueTask, get_issue
from methods.auth import get_user


class State(Enum):
    task_choose = auto()
    task_process = auto()


def handle_hw(bot, update: Update, user_data):
    user = get_user(update.message)

    if not user:
        update.message.reply_text('Not logged in')
        return ConversationHandler.END

    user_data['user'] = user

    q = [QueueTask(t) for t in get_check_queue(user.sid)]

    tasks = [('task#{}'.format(t.id),
              '{} -- {}'.format(t.task_title, t.student_name)) for t in q]

    user_data['tasks'] = {t.id: t for t in q}

    keyboard = [[InlineKeyboardButton(t, callback_data=i)]
                for i, t in tasks]

    markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Выберите задание на проверку',
                              reply_markup=markup)
    return State.task_choose


process_kb = (("На проверке", 3), ("На доработке", 4), ("Зачтено", 5))


def on_choose(bot, update: Update, user_data):
    query: CallbackQuery = update.callback_query
    user: LyceumUser = user_data['user']

    task, iid = query.data.split('#')
    if task != 'task':
        return

    task = user_data['tasks'][int(iid)]
    user_data['task'] = task
    task_url = '\nhttps://lms.yandexlyceum.ru/issue/{}'.format(task.id)

    stud = task.student_url
    stud_name = task.student_name

    descr, comments, token = get_issue(user.sid, iid)
    query.message.reply_text(descr + task_url)

    user_data['token'] = token

    pyfiles = [f for c in comments for f in c.files
               if c.author_href == stud and f.endswith('.py')]

    if not pyfiles:
        query.message.reply_text('Нету файлов!')

    r = requests.get(pyfiles[-1])

    keyboard = ReplyKeyboardMarkup([(i for i, j in process_kb)],
                                   one_time_keyboard=True)

    query.message.reply_text('Автор: {}\nРешение:\n'
                             '```\n{}\n```'.format(stud_name, r.text),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=keyboard)

    return State.task_process


def on_process(bot, update: Update, user_data):
    '''"csrfmiddlewaretoken=iPTiuyP6wvLCKlKJwNkR1WOKUtVJK8N1&form_name=status_form&status=3&comment_verdict="'''
    message: Message = update.message
    pk = dict(process_kb)
    if message.text not in pk:
        # TODO comment
        return ConversationHandler.END

    user: LyceumUser = user_data['user']
    task: QueueTask = user_data['task']

    r = requests.post('https://lms.yandexlyceum.ru/issue/{}'.format(task.id),
                      data=dict(csrfmiddlewaretoken=user_data['token'],
                                comment_verdict='',
                                form_name='status_form',
                                status=pk[message.text]),
                      cookies={'sessionid': user.sid,
                               'csrftoken': user_data['token']})
    print(r.text)
    message.reply_text('Отправлено: ' + message.text)

    return ConversationHandler.END



def add_handlers(dispatcher: Dispatcher):
    dispatcher.add_handler(CommandHandler('hw', handle_hw,
                                          Filters.private,
                                          pass_user_data=True))
    dispatcher.add_handler(CallbackQueryHandler(on_choose,
                                                pass_user_data=True))


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('hw', handle_hw,
                                 Filters.private,
                                 pass_user_data=True)],
    states={
        State.task_choose: [CallbackQueryHandler(on_choose,
                                                 pass_user_data=True)],
        State.task_process: [MessageHandler(Filters.text,
                                            on_process,
                                            pass_user_data=True)]
    },
    fallbacks=[]
)
