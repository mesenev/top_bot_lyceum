import asyncio
import logging
import traceback
from enum import Enum
from json.decoder import JSONDecodeError
from typing import List, Union, Callable

import requests

from config import HOME_LINK
from .json_model import AnnotatedJson
from .parser import Parser as HtmlParser, Tag

logger = logging.getLogger('issue')


class QueueTask(AnnotatedJson):
    id: int
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

    def __eq__(self, other):
        return self.id == other.id


class Comment(object):
    author: str = ''
    author_href: str = ''
    text: str = ''
    files: List[str] = None


class IssueParser(HtmlParser):
    task: str = None
    comments: List[Comment] = None
    current_comment: Comment = None
    token: str = None
    mark: [int, int] = None

    _mark_found = None

    def on_feed(self):
        self.task = ''
        self.comments = []
        self._mark_found = False

    def on_starttag(self, t: Tag):
        if (t.attrs.get('name') == 'csrfmiddlewaretoken'
                and self._tags_stack[-2].attrs.get('id') == 'status_form'):
            self.token = t.attrs['value']

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
            elif t.name == 'a':
                data = ' [{}]({})'.format(data, t.attrs.get('href', ''))
            else:
                data = ' ' + data

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
        elif t.name == 'a' and data == 'Оценка':
            self._mark_found = True
        elif self._mark_found and 'accordion2-result' in t.classes:
            self.mark = list(map(float, data.split('из')))

    def on_endtag(self, t: Tag):
        if self.current_comment is not None and t.name == 'li':
            self.comments.append(self.current_comment)
            self.current_comment = None
        elif self._mark_found and t.name == 'div' and 'card' in t.classes:
            self._mark_found = False


def get_check_queue(sid: str, n: int = 5):
    url = '{}/course/ajax_get_queue?' \
          'draw=2&start.py=0&length={}&lang=ru&timezone=Asia%2FVladivostok&' \
          'course_id=34&' \
          'filter=status_field%3D3'.format(HOME_LINK, n)

    with requests.Session() as s:
        data = s.get(url, cookies={'sessionid': sid})

    try:
        j = data.json()
    except JSONDecodeError as e:
        return []

    return j['data']


def get_issue(sid: str, issue_id: int) -> [str, List[Comment], str]:
    url = HOME_LINK + '/issue/' + str(issue_id)

    print('--> Start download issue id', issue_id)
    r = requests.get(url, cookies={'sessionid': sid})

    parser = IssueParser()
    parser.feed(r.text)
    parser.close()
    print('<-- Finished download issue id', issue_id)

    return parser.task, parser.comments, parser.token, parser.mark


loop = asyncio.get_event_loop()


def get_issue_async(sid: str, issue_id: int):
    try:
        return loop.run_in_executor(None, get_issue, sid, issue_id)
        # return get_issue(sid, issue_id)
    except:
        logger.error(traceback.format_exc())


class VerdictType(Enum):
    status = 'status', 'status_form'
    mark = 'mark', 'mark_form'


Verdict = Union[int, float]


def issue_send_verdict(sid: str, token: str, issue_id: int,
                       comment: str,
                       verdict_type: VerdictType,
                       verdict: Verdict,
                       on_finish: Callable):
    verdict_key, form_name = verdict_type.value
    form_data = dict(csrfmiddlewaretoken=token,
                     comment_verdict=comment,
                     form_name=form_name)
    form_data[verdict_key] = verdict

    if verdict_type == VerdictType.mark:
        form_data['Accepted'] = ''

    try:
        url = '{}/issue/{}'.format(HOME_LINK, issue_id)
        r = requests.post(url,
                          data=form_data,
                          cookies={'sessionid': sid,
                                   'csrftoken': token})
        logger.debug(r.text)
    except Exception as e:
        logger.log(logging.ERROR,
                   'request send failed. '
                   'id: {} session: {} token: {} comment: {} '
                   'verdict: {}'.format(issue_id, sid, token,
                                        comment, verdict))
    else:
        logger.info('verdict sent. '
                     'id: {}, status: {}'.format(issue_id, r.status_code))

        on_finish(r.status_code)
