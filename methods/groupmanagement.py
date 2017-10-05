import random

from config_default import CONTRIBUTORS
from database import LyceumGroup, Student


def create_group(bot, update):
    if update.message.from_user.id not in CONTRIBUTORS:
        bot.send_message(chat_id=update.message.chat_id, text=random.choice(DENIED)
                         .format(update.message.from_user.first_name))
        return
    try:
        params = [x.strip(' \t\n') for x in update.message.split('\n')[1:]]

        if len(params):
            bot.send_message(chat_id=update.message.chat_id, text=INSTRUCTION)

        group = group_create(bot, *params)
        bot.send_message(chat_id=update.message.chat_id, text=random.choice(SUCCESS_GROUP))

        st = students_create(group)
        bot.send_message(chat_id=update.message.chat_id, text='Создание %i студентов завершено успешно' % len(st))
        message = 'Служба создания групп желает вам хорошего дня!'
    except Exception as e:
        message = 'Что-то пошло не так. Обратитесь к @mesenev с вот этим:\n' + str(e)

    bot.send_message(chat_id=update.message.chat_id, text=message)


def students_create(group, *argv):
    created = []
    for name in argv:
        student = Student()
        student.fullname = name
        student.lyceum_group = group
        student.save()
        created.append(student.fullname)
    return created


def group_create(bot, *args):
    group = LyceumGroup()
    group.alias = args[0]
    group.telegram_chat_id = args[1]
    group.lecturer_telegram_id, group.lecturer_fullname = [x.strip(' \t\n') for x in args[2].split(',')]
    group.city = args[3]
    group.save()
    return group


def approve_registration(bot, update):
    if update.message.from_user.id not in CONTRIBUTORS:
        return
    try:
        st_id = update.message.split()[1]
        student = Student.get(str(Student.id) == st_id)
        student.approved = True
        student.save()
        bot.send_message(chat_id=update.message.chat_id,
                         text='Регистрация студента {} подтверждена.'.format(student.fullname))
    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Подтверждение упало с ошибкой: \n %s' % str(e))
    pass


DENIED = [
    'Похоже, у вас не хватает прав доступа, {}.',
    'Вам сюда нельзя. Ваша фамилия будет записана, на всякий случай.',
]

SUCCESS_GROUP = [
    'Группа успешно создана! Перехожу к созданию объектов пользователей.'
]

INSTRUCTION = 'Some text'
