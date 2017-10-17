import telegram

custom_keyboard = [['/login', '/hw']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                            resize_keyboard=True)


# TODO: Исправить приветствие. Его могут видеть как студенты так и
# преподаватели.
def on_start(bot, update):
    update.message.reply_text("Велкам! Для начала залогиньтесь "
                              "(если вы ещё не)."
                              " Потом проверьте домашки. "
                              "/top пока не работает, "
                              "но скоро заработает.",
                              reply_markup=reply_markup)
