from json.decoder import JSONDecodeError
from typing import List

import requests

from .json_model import AnnotatedJson
from .parser import Parser as HtmlParser, Tag


class QueueTask(AnnotatedJson):
    responsible_name: str
    has_issue_access: str
    issue_url: str
    responsible_url: str
    status_name: str
    student_name: str
    student_url: str
    task_title: str

    @staticmethod
    def _extract_id(data, field_name):
        return data['DT_RowData'].get(field_name)


class Comment(object):
    author: str = ''
    author_href: str = ''
    text: str = ''
    files: List[str] = None


class IssueParser(HtmlParser):
    task: str = None
    comments: List[Comment] = None
    current_comment: Comment = None

    def on_feed(self):
        self.task = ''
        self.comments = []

    def on_starttag(self, t: Tag):
        if t.name == 'li' and 'history' in self._classes:
            self.current_comment = Comment()
            self.current_comment.files = []

    def on_data(self, t: Tag, data: str):
        in_problem = ('problem-statement' in self._classes
                      and 'modal' not in self._classes)
        in_header = 'header' in self._classes

        comment = self.current_comment

        comment_classes = ('contest-response-comment',
                           'issue-page-comment')

        if in_problem and not in_header:
            data = ' '.join(data.split())
            if 'tex-monospace' in t.classes:
                data = "```\n" + data + "\n```\n"

            self.task += data
        elif (t.name == 'a'
              and 'card-link' in t.classes
              and 'user_img' not in self._classes
              and comment is not None):
            comment.author_href = t.attrs.get('href')
            comment.author = data
        elif comment is not None:
            if any(c in self._classes for c in comment_classes):
                comment.text += data
            elif t.name == 'a' and 'files' in self._classes:
                comment.files.append(t.attrs['href'])

    def on_endtag(self, t):
        if self.current_comment is not None and t.name == 'li':
            self.comments.append(self.current_comment)
            self.current_comment = None


issue_parser = IssueParser()


def get_check_queue(sid: str, n: int = 5):
    url = 'https://lms.yandexlyceum.ru/course/ajax_get_queue?' \
          'draw=2&start=0&length={}&lang=ru&timezone=Asia%2FVladivostok&' \
          'course_id=34&' \
          'filter=status_field%3D3'.format(n)

    s = requests.Session()
    data = s.get(url, cookies={'sessionid': sid})
    try:
        j = data.json()
    except JSONDecodeError as e:
        return {}

    return j['data']


def get_issue(sid: str, issue_id: int):
    data = requests.get('https://lms.yandexlyceum.ru/issue/' + str(issue_id),
                        cookies={'sessionid': sid}).text

    issue_parser.feed(data)
    issue_parser.close()

    return issue_parser.task, issue_parser.comments
