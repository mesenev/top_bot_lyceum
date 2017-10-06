import random

from database import Student, LyceumGroup


def send_notification_to_lecturer(bot, whois, student):
    msg = '{} хочет зарегистрироваться как {} id:{},\n'.format(whois.firstname,
                                                               whois.lastname,
                                                               student.fullname,
                                                               whois.id)
    msg += 'Для подтверждения отправьте комманду /approve %s,\n' % student.id
    msg += 'хорошего дня.'
    bot.send_message(chat_id=student.lyceum_group.lecturer_telegram_id, text=msg)


def student_registration(bot, update):
    params = [x.strip(' \t\n') for x in update.message.split('\n')[1:]]
    whois = update.message.from_user
    if len(params):
        bot.send_message(chat_id=update.message.chat_id, text=random.choice(INSTRUCTION))
        return

    student = Student.get(telegram_id=whois.id)
    if student:
        bot.send_message(chat_id=update.message.chat_id, text=random.choice(ALREADY))
        return

    all_kids = Student.filter()
    if params[0] not in [x.fullname for x in all_kids]:
        bot.send_message(chat_id=update.message.chat_id, text=random.choice(NO_SUCH))
        return

    student = Student.get(fullname=params[0]).join(LyceumGroup)
    student.telegram_id = whois.id
    student.approved = False
    send_notification_to_lecturer(bot, whois, student)
    bot.send_message(chat_id=update.message.chat_id, text=random.choice(APPROVE_WAIT))


INSTRUCTION = ''
SUCCESS = [
    'Вы успешно зарегистрированы! 🎉'
]
ALREADY = [
    '...Что значит повторно зарегистрироваться? Повторно не регистрируем! Когда будем? Никогда! Жалуйтесь кому хотите.',
]
NO_SUCH = [
    'Такого в списках нет, перепроверьте запись! А ещё лучше скопируйте с сайта правильно - наши списки от туда'
]
APPROVE_WAIT = [
    'Ждите теперь подвтерждения о регистрации. Сколько? Сорок дней максимум.'
]