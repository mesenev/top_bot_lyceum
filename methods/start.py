import datetime

import telegram

from config import CUPS_OF

custom_keyboard = [['/login', '/hw', '/top']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                            resize_keyboard=True)


# TODO: Исправить приветствие. Его могут видеть как студенты так и
def on_start(bot, update):
    update.message.reply_text("Велкам! Для начала залогиньтесь "
                              "(если вы ещё не)."
                              " Потом проверьте домашки. "
                              "/top покажет лидеров",
                              reply_markup=reply_markup)


def send_startup_greeting(bot, chat_id):
    now = datetime.datetime.now().strftime("%B %d, %H:%M")
    text_fmt = ('Successfully launched! '
                'Current time is:{} \n'
                ' Cups of tea: {}')
    bot.send_message(chat_id=chat_id,
                     text=text_fmt.format(now, CUPS_OF))
