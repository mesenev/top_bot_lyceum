import telegram

from database import Task, Student


def send_msg(bot: telegram.Bot, update: telegram.Update):
    data = update.message.split()[1:]
    if len(data) != 0:
        bot.send_message(chat_id=update.message.chat_id, text=SAMPLE)
    if len(data) != 2:
        bot.send_message(chat_id=update.message.chat_id, text=INCORRECT_INPUT)

    message = get_task(data[0], data[1], update.message.from_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=message)
    pass


def get_task(lesson, tasknum, student_id):
    student = Student.select().where(Student.telegram_id == student_id)
    task = Task.select().where((Task.lyceum_group == student.lyceum_group) &
                               (Task.lesson == lesson) &
                               (Task.number == tasknum))
    if not task:
        add_tasks_from_lesson(lesson)
        return msg
    return msg


def add_tasks_from_lesson(leson):
    list = get_urls_tasks_list(lesson)


def get_urls_tasks_list(lesson):

    l = []
    return l


INCORRECT_INPUT = ['Не могу понять, что вы от меня хотите']
SAMPLE = '/task УРОК НОМЕР'
