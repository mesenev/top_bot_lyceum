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
        group = group_create(bot, *params)
        bot.send_message(chat_id=update.message.chat_id, text=random.choice(SUCCESS_GROUP))

        st = students_create(group)
        bot.send_message(chat_id=update.message.chat_id, text='Создание %i студентов завершено успешно' % len(st))
        message = 'Служба создания групп желает вам хорошего дня!'
    except Exception as e:
        message = 'Что-то пошло не так. Обратитесь к @mesenev с вот этим:\n'+str(e)

    bot.send_message(chat_id=update.message.chat_id, text = message)


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


DENIED = [
    'Похоже, у вас не хватает прав доступа, {}.',
    'Вам сюда нельзя. Ваша фамилия будет записана, на всякий случай.',
]

SUCCESS_GROUP = [
    'Группа успешно создана! Перехожу к созданию объектов пользователей.'
]