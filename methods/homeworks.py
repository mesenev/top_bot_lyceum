from asyncio.futures import Future
from enum import Enum, auto
from typing import NamedTuple, List, Dict

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
from lyceum_api.issue import QueueTask, loop, get_issue_async, issue_send_verdict
from methods.auth import get_user


class State(Enum):
    task_choose = auto()
    task_process = auto()


class Tasks(NamedTuple):
    mapping: Dict[int, QueueTask]
    order: List[QueueTask]
    futures: Dict[int, Future]


def send_msg_by_chunks(msg: Message,
                       text: str,
                       delim: str,
                       parse_mode=None,
                       keyboard=None):
        chunks = ['']
        for t in text.split(delim):
            if len(chunks[-1] + t) + 3 < 4096:
                chunks[-1] += '\n' + t
            else:
                chunks[-1] += '```'
                chunks.append('```' + t)

        for reply in chunks:
            msg.reply_text(reply,
                           parse_mode=parse_mode,
                           reply_markup=keyboard)


def handle_hw(bot, update: Update, user_data, prev_task: QueueTask=None):
    user = get_user(update.message)

    if not user:
        update.message.reply_text('Not logged in')
        return ConversationHandler.END

    user_data['user'] = user

    tasks = user_data.get('tasks')
    if not tasks or len(tasks.order) < 10:
        q = [QueueTask(t) for t in get_check_queue(user.sid, 30)]

        user_data['tasks'] = Tasks({t.id: t for t in q},
                                   q,
                                   {t.id: get_issue_async(user.sid, t.id)
                                    for t in q})
    else:
        q = user_data['tasks'].order

    if prev_task:
        del tasks.mapping[prev_task.id]
        del tasks.futures[prev_task.id]
        tasks.order.remove(prev_task)

    if not q:
        update.message.reply_text('Ура! Домашки проверены'
                                  if prev_task else
                                  'Пока что домашек нет...')
        return ConversationHandler.END

    tasks = [('task#' + str(t.id),
              '{} -- {}'.format(t.task_title, t.student_name))
             for t in q[:7]]
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

    task, tid = query.data.split('#')
    if task != 'task':
        return ConversationHandler.END

    tid = int(tid)
    tasks: Tasks = user_data['tasks']
    task: QueueTask = tasks.mapping.get(tid)

    if not task:
        return ConversationHandler.END

    user_data['task'] = task
    task_url = '\nhttps://lms.yandexlyceum.ru/issue/{}'.format(task.id)

    stud = task.student_url
    stud_name = task.student_name

    descr, comments, token = loop.run_until_complete(tasks.futures[tid])
    query.message.reply_text(descr + task_url,
                             parse_mode=ParseMode.MARKDOWN)

    user_data['token'] = token

    kb = [(i for i, j in process_kb)]

    pyfiles = [f for c in comments for f in c.files
               if c.author_href == stud and f.endswith('.py')]

    if not pyfiles:
        kb.append(['Решения надо отправлять в файлах с расширением .py'])
        if [f for c in comments for f in c.files if c.author_href == stud]:
            text = 'Нету файлов .py!'
        else:
            c_text = ['{}:\n{}'.format(c.author, c.text) for c in comments]
            text = 'Нету файлов совсем! Комментарии:\n' + '\n\n'.join(c_text)
    else:
        r = requests.get(pyfiles[-1])
        r.encoding = 'utf-8'

        text = ('Автор: {}\nРешение:\n'
                '```\n{}\n```'.format(stud_name, r.text))

    keyboard = ReplyKeyboardMarkup(kb,
                                   one_time_keyboard=True,
                                   resize_keyboard=True)

    send_msg_by_chunks(query.message, text, '\n',
                       parse_mode=ParseMode.MARKDOWN,
                       keyboard=keyboard)

    return State.task_process


def on_process(bot, update: Update, user_data):
    message: Message = update.message
    pk = dict(process_kb)
    if message.text not in pk:
        user_data['comment'] = message.text
        message.reply_text('Комментарий принят. Теперь вердикт.')
        return State.task_process

    user: LyceumUser = user_data['user']
    task: QueueTask = user_data['task']

    loop.run_in_executor(None,
                         issue_send_verdict,
                         user.sid,
                         user_data['token'],
                         task.id,
                         pk[message.text],
                         user_data.get('comment', ''),
                         lambda: message.reply_text('Отправлено: '
                                                    + message.text))
    user_data['comment'] = ''

    tasks: Tasks = user_data['tasks']

    return handle_hw(bot, update, user_data, prev_task=task)


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
