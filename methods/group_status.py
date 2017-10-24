import requests
from telegram import Bot, Update

from config import config
from database import LyceumUser
from lyceum_api.parser import Parser, Tag
from methods.auth import get_user


def get_status(bot: Bot, update: Update):
    user:LyceumUser = get_user(update.message)
    if not user or not user.is_teacher:
        update.message.reply_text('Очевидно, вы должны быть преподавателм и авторизованы')
    bot.send_message(chat_id=update.message.chat_id, text="Собираем статистику на группу...")
    for link in user.course_links:
        lesson_links = get_links_to_available_lessons(config.DATA_URL.format(link), user.token)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Список пройденных по курсу {} "
                              "уроков получен. Обрабатываю...".format(link))

    return


def get_links_to_available_lessons(link, token):
    req = requests.get(link, cookies={'sessionid': token})
    parser = GradebookParser()
    parser.feed(req.content.decode())
    return parser.get_links(), parser


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
