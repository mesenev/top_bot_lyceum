import re
from asyncio.futures import Future
from enum import Enum, auto
from functools import partial
from typing import NamedTuple, List, Dict

import requests
from PIL import Image
from telegram.callbackquery import CallbackQuery
from telegram.ext import CommandHandler, MessageHandler, Filters, RegexHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton as Button
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.message import Message
from telegram.parsemode import ParseMode
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.replykeyboardremove import ReplyKeyboardRemove
from telegram.update import Update

from config import HOME_LINK
from database.LyceumUser import LyceumUser
from lyceum_api import get_check_queue
from lyceum_api.issue import QueueTask, loop, get_issue_async, issue_send_verdict, VerdictType, Verdict
from methods.auth import get_user
from methods.start import reply_markup as greeting_markup
from methods.style import hl_code, Style

FLOATS = r'(\d+(?:.\d+)?)'


class State(Enum):
    task_choose = auto()
    task_process = auto()
    enter_mark = auto()


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
    # TODO: store in database
    user_data.setdefault('style', Style())

    if not user:
        update.message.reply_text('Not logged in')
        return ConversationHandler.END

    user_data['user'] = user

    tasks: Tasks = user_data.get('tasks')
    if not tasks or len(tasks.order) < 8:
        update.message.reply_text('Запрашиваем данные...',
                                  reply_markup=ReplyKeyboardRemove())
        q = [QueueTask(t) for t in get_check_queue(user.sid, 8)]

        futures = tasks.futures if tasks else {}
        futures.update({t.id: get_issue_async(user.sid, t.id)
                       for t in q if t.id not in futures})
        tasks = Tasks({t.id: t for t in q}, q, futures)
        user_data['tasks'] = tasks
    else:
        q = tasks.order

    if prev_task and prev_task.id in tasks.mapping:
        del tasks.mapping[prev_task.id]
        del tasks.futures[prev_task.id]
        tasks.order.remove(prev_task)

    if not q:
        update.message.reply_text('Ура! Домашки проверены'
                                  if prev_task else
                                  'Пока что домашек нет...',
                                  reply_markup=greeting_markup)
        return ConversationHandler.END

    tasks = [('task#' + str(t.id),
              '{} -- {}'.format(t.task_title, t.student_name))
             for t in q[:7]]
    keyboard = [[Button(t, callback_data=i)]
                for i, t in tasks]

    markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Выберите задание на проверку',
                              reply_markup=markup)
    return State.task_choose


ACCEPT, DECLINE, SKIP = "Зачтено на {:g}", "На доработку", "Пропустить"
DECLINE_ID = 4
ACCEPT_RE = ('{}'.join(map(re.escape,
                           ACCEPT.split('{:g}'))).format(FLOATS)
             + '|' + FLOATS)


def on_choose(bot, update: Update, user_data):
    query: CallbackQuery = update.callback_query

    task, tid = query.data.split('#')
    if task != 'task':
        return ConversationHandler.END

    tid = int(tid)
    tasks: Tasks = user_data['tasks']
    task: QueueTask = tasks.mapping.get(tid)
    style: Style = user_data['style']

    if not task:
        return ConversationHandler.END

    task_url = '\n{}/issue/{}'.format(HOME_LINK, task.id)

    stud = task.student_url
    stud_name = task.student_name

    result = loop.run_until_complete(tasks.futures[tid])

    descr, comments, token, (mark, max_mark) = result

    variants = [DECLINE, SKIP, ACCEPT.format(max_mark), '...']

    user_data['task'] = task
    user_data['token'] = token
    user_data['max_mark'] = max_mark
    user_data['variants'] = set(variants)

    kb = [variants]
    descr_kb = [[]]

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

        text = 'Автор: {}'.format(stud_name)
        user_data['solution'] = r.text
        if style.show_text:
            text += '\nРешение:\n```\n{}\n```'.format(r.text)
            descr_kb[0] = [Button('Загрузить решение с подсветкой',
                                  callback_data='get_img')]

    mark_text = '\n\nОценка: {:g} из {:g}'.format(mark, max_mark)
    query.message.reply_text(descr + task_url + mark_text,
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=InlineKeyboardMarkup(descr_kb,
                                                               one_time_keyboard=True))

    keyboard = ReplyKeyboardMarkup(kb,
                                   one_time_keyboard=True,
                                   resize_keyboard=True)

    if pyfiles and not style.show_text:
        reply_with_code(query.message, user_data, text, keyboard)
    else:
        send_msg_by_chunks(query.message, text, '\n',
                           parse_mode=ParseMode.MARKDOWN,
                           keyboard=keyboard)


    return State.task_process


def reply_with_code(msg: Message, user_data, caption=None, kbd=None):
    task: QueueTask = user_data['task']
    code: str = user_data['solution']

    img = hl_code(code, task.id, user_data)

    reply = msg.reply_document
    if user_data['style'].format in ['png', 'jpg']:
        im = Image.open(img)
        width, height = im.size
        img.seek(0)

        if max(width, height) <= 1280:
            reply = msg.reply_photo

    reply(img, caption=caption, reply_markup=kbd)


def on_get_img(bot, update: Update, user_data):
    query: CallbackQuery = update.callback_query

    if query.data != 'get_img':
        return State.task_process

    reply_with_code(query.message, user_data)
    return State.task_process


def on_verdict_sent(msg: Message, reply: str, result: int):
    msg.reply_text('Something went wrong... '
                   'Please contact developers'
                   if result == 500 else reply)


def send_verdict(msg: Message,
                 user_data,
                 verdict_type: VerdictType,
                 verdict: Verdict,
                 reply: str):
    user: LyceumUser = user_data['user']
    task: QueueTask = user_data['task']

    send = partial(loop.run_in_executor, None, issue_send_verdict)

    send(user.sid,
         user_data['token'],
         task.id,
         user_data.get('comment', ''),
         verdict_type,
         verdict,
         partial(on_verdict_sent, msg, reply))


def on_process(bot, update: Update, user_data):
    user_data['comment'] = ''
    return handle_hw(bot, update, user_data, prev_task=user_data['task'])


def on_decline(bot, update: Update, user_data):
    send_verdict(update.message,
                 user_data,
                 VerdictType.status,
                 DECLINE_ID,
                 'Отправлено: ' + DECLINE)
    return on_process(bot, update, user_data)


def on_accept(bot, update: Update, user_data):
    text = update.message.text

    mark = ''.join(re.findall(ACCEPT_RE, text)[0])

    send_verdict(update.message,
                 user_data,
                 VerdictType.mark,
                 float(mark),
                 'Выставлена оценка: ' + mark)
    return on_process(bot, update, user_data)


def on_comment(bot, update: Update, user_data):
    message: Message = update.message
    user_data['comment'] = message.text
    message.reply_text('Комментарий принят. Теперь вердикт.')
    return State.task_process


def on_mark(bot, update: Update, user_data):
    msg: Message = update.message
    max_mark = int(user_data['max_mark'])
    kb = [list(map(str, range(max_mark//5, max_mark, max_mark//5)))]

    msg.reply_text('Выберите оценку, или введите свою',
                   reply_markup=ReplyKeyboardMarkup(kb, True, True))
    return State.task_process


hw_handler = CommandHandler('hw', handle_hw,
                            Filters.private,
                            pass_user_data=True)

conv_handler = ConversationHandler(
    entry_points=[hw_handler],
    states={
        State.task_choose: [CallbackQueryHandler(on_choose,
                                                 pass_user_data=True)],
        State.task_process: [RegexHandler('^{}$'.format(SKIP),
                                          handle_hw,
                                          pass_user_data=True),
                             RegexHandler('^{}$'.format(ACCEPT_RE),
                                          on_accept,
                                          pass_user_data=True),
                             RegexHandler('^{}$'.format(DECLINE),
                                          on_decline,
                                          pass_user_data=True),
                             RegexHandler('^\.\.\.$',
                                          on_mark,
                                          pass_user_data=True),
                             MessageHandler(Filters.text,
                                            on_comment,
                                            pass_user_data=True),
                             CallbackQueryHandler(on_get_img,
                                                  pass_user_data=True)]
    },
    fallbacks=[hw_handler]
)
