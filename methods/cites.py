import random

import config


def answers(bot, update, **kwargs):
    update.message.reply_text(random.choice(config.ANSWERS))