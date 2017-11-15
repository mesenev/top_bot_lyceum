import config


def answers(bot, update, **kwargs):
    update.message.reply_text(config.ANSWERS)