from enum import Enum, auto

from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext.conversationhandler import ConversationHandler
from telegram.message import Message
from telegram.update import Update
from lyceum_api import get_check_queue
from lyceum_api.issue import QueueTask
from methods.auth import get_user


class State(Enum):
    not_logged_in = auto()

def handle_hw(bot, update: Update):
    user = get_user(update.message)

    if not user:
        update.message.reply_text('Not logged in')
        return ConversationHandler.END

    q = [QueueTask(t) for t in get_check_queue(user.sid)]

    tasks = ('Задания на проверку:\n' +
             '\n'.join('{} -- {}'.format(t.task_title, t.student_name) for t in q))

    update.message.reply_text(tasks)
    return ConversationHandler.END


# def on_choose(bot, update):
#     message: Message = update.message


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('hw', handle_hw, Filters.private)],
    states={
    #     States.username: [MessageHandler(Filters.text,
    #                                      handle_username,
    #                                      pass_user_data=True)],
    #     States.password: [MessageHandler(Filters.text,
    #                                      handle_password,
    #                                      pass_user_data=True)]
    },
    fallbacks=[]
)
