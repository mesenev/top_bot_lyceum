import random
from database import Student
from methods.common import get_common_data_from_web


def send_msg(bot, update):
    message, is_success = create_message(update)
    bot.send_message(chat_id=update.message.chat_id, text=message)


def create_message(update):
    student = Student.get(telegram_id=update.message.from_user.id)
    if not student:
        return random.choice(NOT_REGISTERED), False
    rating = get_common_data_from_web(student.lyceumgroup_id)
    position = find_kid_position(rating, student.fullname)

    message = random.choice(HEADERS).format(student.fullname) + '\n'
    pos = str(position[0]) if position[0] == position[1] else '{}--{}'.format(position[0], position[1])
    message += 'Вы занимате {} позицию из {}, с рейтингом {}\n'.format(pos, len(rating), position[2])
    message += random.choice(POSTWORDS).format(student.fullname)

    return message, True


def find_kid_position(rating, name):
    rate_dict = {}
    score = -1
    for kid in rating:
        rate_dict[kid[1]] = rate_dict.get(kid[1], default=[]) + [kid[0]]
        if kid[0] == name:
            score = kid[1]
    if score == -1:
        raise StudentNotFoundException(name)
    position = 1
    for rating in sorted(rate_dict.keys(), reverse=True):
        if name in rate_dict[rating]:
            return position, len(rate_dict[rating]), score
        position += len(rate_dict[rating])


class StudentNotFoundException(BaseException):
    def __init__(self, student_name):
        self.name_not_found = student_name


NOT_REGISTERED = [
    'Вашей фамилии у нас нет. Вы вообще учитесь? Обратитесь в отдел /register',
    'Вас нет в списках. Возможно, у вас получится исправить это через команду /register'
]

HEADERS = [
    'Здравствуй {}.',
    'Сейчас мы это выясним',
    'Как? "{}"?',
]

POSTWORDS = [
    'Распишитесь вот здесь.',
    'Ещё что-нибудь?',
    'Обращайтесь, если что',
]

