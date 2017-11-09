import random
from config import CONTRIBUTORS


def send_msg(bot, update):
    coming_msg = ''.join(filter(str.isalpha, update.message.text.lower()))
    message = ''
    if coming_msg == 'приветбот' or coming_msg == 'приветствуюбот':
        message = greeting(update)
    if 'можно' in coming_msg.split():
        message = mojno(update)
    if message:
        bot.send_message(chat_id=update.message.chat_id, text=message)


def greeting(update):
    if update.message.from_user.id in CONTRIBUTORS:
        return random.choice(GREETING_TO_CONTRIBUTOR)
    return random.choice(GREETING_TO_SOMEONE).format(name=update.message.from_user.first_name)


def mojno(update):
    if update.message.from_user.id in CONTRIBUTORS:
        return random.choice(ALLOW_TO_CONTRIBUTOR)
    return random.choice(ALLOW_TOSOMEONE_ELSE).format(name=update.message.from_user.first_name)


ALLOW_TO_CONTRIBUTOR = ['Вам, конечно, можно, создатель']
ALLOW_TOSOMEONE_ELSE = ['Нет, вас за это точно отчислят']
GREETING_TO_CONTRIBUTOR = [
    'Здравствуй, создатель',
]
GREETING_TO_SOMEONE = [
    'Приветствую, {name}',
]
