from collections import defaultdict, Counter
import requests
from telegram import Bot, Update

from config import config, HOME_LINK
from database import LyceumUser
from lyceum_api.parser import Parser, Tag
from methods.auth import get_user


def get_summary(bot: Bot, update: Update):
    user: LyceumUser = get_user(update.message)
    if not user or not user.is_teacher:
        update.message.reply_text('Очевидно, вы должны быть преподавателм и авторизованы')
    bot.send_message(chat_id=update.message.chat_id, text="Собираем статистику на группу...")
    for course in set(user.course_links.split(',')):
        lesson_links = get_links_to_available_lessons(config.DATA_URL.format(course), user.sid)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Список пройденных по курсу {} уроков получен. "
                         "Их всего {}. Обработка может занять некоторое время. За работу..."
                         .format(course, len(lesson_links)))
        overall = defaultdict(Counter)
        for link in lesson_links:
            _ = get_lesson_data(HOME_LINK + link, user.sid)
            for student, data in _:
                overall[student].update(data)
        msg = ''
        idx = 1
        for i in overall.items():
            _ = i[1]['done'], i[1]['failed'], i[1]['pending'], i[1]['untouched']
            msg += '{}. {}: D:{} F:{} P:{} U:{}\n'.format(idx, i[0], *_)
            idx += 1
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    return


def get_links_to_available_lessons(link, token):
    req = requests.get(link, cookies={'sessionid': token})
    parser = GradebookParser()
    parser.feed(req.content.decode())
    return parser.get_links()


def get_lesson_data(link, token):
    req = requests.get(link, cookies={'sessionid': token})
    parser = LessonParser()
    parser.feed(req.content.decode())
    return parser.get_lesson_data()


class GradebookParser(Parser):
    lessons_links = []
    in_table = False

    def on_feed(self):
        pass

    def on_starttag(self, t: Tag):
        if t.name == 'table':
            self.in_table = True

        if self.in_table and t.name == 'a':
            self.lessons_links.append(t.attrs['href'])

    def on_endtag(self, t: Tag):
        if t.name == 'table':
            self.in_table = False

    def get_links(self):
        res = []
        for x in self.lessons_links:
            if not (x[0] == '#' or 'javascript' in x or 'users' in x):
                res.append(x)
        return set(res)


class LessonParser(Parser):
    students_data = []
    in_tr = False
    is_student_full_name_tag = False
    to_add = None

    @staticmethod
    def default_dict():
        return {'done': 0, 'failed': 0, 'pending': 0, 'untouched': 0}

    def on_feed(self):
        self.students_data = []
        self.in_tr = False
        self.is_student_full_name_tag = False
        self.to_add = None

    def on_starttag(self, t: Tag):
        if t.name == 'tr':
            self.in_tr = True

        if self.in_tr and t.name == 'a' and 'users' in t.attrs['href']:
            self.is_student_full_name_tag = True

        if self.in_tr and t.name == 'span' and 'label' in t.classes and 'style' in t.attrs.keys() and 'background-color' in \
                t.attrs['style']:
            if '#5CB85C' in t.attrs['style']:
                self.to_add[1]['done'] += 1
            elif '#D9534F' in t.attrs['style']:
                self.to_add[1]['failed'] += 1
            elif '#F0AD4E' in t.attrs['style']:
                self.to_add[1]['pending'] += 1
            elif '#818A91' in t.attrs['style']:
                self.to_add[1]['untouched'] += 1

    def on_data(self, t: Tag, data: str):
        if t.name == 'a' and self.is_student_full_name_tag:
            self.to_add = (data, self.default_dict())
            self.is_student_full_name_tag = False

    def on_endtag(self, t: Tag):
        if self.in_tr and t.name == 'tr':
            self.in_tr = False
            if self.to_add:
                self.students_data.append(self.to_add)
            self.to_add = None

    def get_lesson_data(self):
        return self.students_data
