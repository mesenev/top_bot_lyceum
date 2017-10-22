from telegram import Update


def on_raise(bot, update: Update):
    raise Exception()