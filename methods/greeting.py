import random
from config import *


def greeting(bot, update):
    coming_msg = ''.join(filter(str.isalpha, update.message.text.lower()))
    if coming_msg == 'приветбот':
        if update.message.from_user.id in CONTRIBUTORS:
            bot.send_message(chat_id=update.message.chat_id, text=random.choice(GREETING_TO_CONTRIBUTOR))
            return
        bot.send_message(chat_id=update.message.chat_id, text=random.choice(GREETING_TO_SOMEONE)
                         .format(name=update.message.from_user.first_name))
    return
