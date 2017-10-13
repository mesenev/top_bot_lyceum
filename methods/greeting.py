import telegram


def on_start(bot, update):
    custom_keyboard = [['/login', '/hw']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard,
                                                resize_keyboard=True)
    update.message.reply_text("Велкам! Для начала залогиньтесь "
                              "(если вы ещё не)."
                              " Потом проверьте домашки. "
                              "/top пока не работает, "
                              "но скоро заработает.",
                              reply_markup=reply_markup)
