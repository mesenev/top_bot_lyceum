import os
import typing
import unittest
from collections import Counter, OrderedDict
from typing import List, Tuple, Any

from lyceum_api import parser
from lyceum_api.issue import IssueParser

dirname = os.path.dirname(__file__)

HtmlState = Tuple[str,
                  str,
                  Tuple[Any],
                  typing.Counter[str],
                  typing.Counter[str]]


class TestParser(parser.Parser):
    def __init__(self):
        super(TestParser, self).__init__()
        self.state: List[HtmlState] = []

    def add_state(self, what, t: parser.Tag):
        self.state.append((what, t.name,
                           tuple(OrderedDict(**t.attrs).items()),
                           +self._classes, +self._tags))

    def on_starttag(self, t: parser.Tag):
        self.add_state('open', t)

    def on_endtag(self, t: parser.Tag):
        self.add_state('close', t)


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.parser = TestParser()

    def tearDown(self):
        del self.parser

    def test_div_with_class(self):
        s = '<div class="a"></div>'
        state = [('open', 'div', (('class', 'a'),),
                  Counter(), Counter()),
                 ('close', 'div', (('class', 'a'),),
                  Counter(), Counter())]

        self.parser.feed(s)
        self.assertListEqual(self.parser.state, state)

    def test_two_tags(self):
        s = ('<div class = "a">'
             '  <x type="y" class="b"></x>'
             '<y type="z" class="c"></y>'
             '</div>')
        state = [('open', 'div', (('class', 'a'),),
                  Counter(), Counter()),
                 ('open', 'x', (('type', 'y'), ('class', 'b')),
                  Counter('a'), Counter({'div': 1})),
                 ('close', 'x', (('type', 'y'), ('class', 'b')),
                  Counter('a'), Counter({'div': 1})),
                 ('open', 'y', (('type', 'z'), ('class', 'c')),
                  Counter('a'), Counter({'div': 1})),
                 ('close', 'y', (('type', 'z'), ('class', 'c')),
                  Counter('a'), Counter({'div': 1})),
                 ('close', 'div', (('class', 'a'),),
                  Counter(), Counter())]

        self.parser.feed(s)
        self.assertListEqual(self.parser.state, state)

    def test_void_elements(self):
        s = ('<div class = "a">'
             '  <x type="y" class="b"><img class="a d"></x>'
             '<y type="z" class="c"></y>'
             '</div>')
        state = [('open', 'div', (('class', 'a'),),
                  Counter(), Counter()),
                 ('open', 'x', (('type', 'y'), ('class', 'b')),
                  Counter('a'), Counter({'div': 1})),
                 ('open', 'img', (('class', 'a d'),),
                  Counter('ab'), Counter(['div', 'x'])),
                 ('close', 'x', (('type', 'y'), ('class', 'b')),
                  Counter('a'), Counter({'div': 1})),
                 ('open', 'y', (('type', 'z'), ('class', 'c')),
                  Counter('a'), Counter({'div': 1})),
                 ('close', 'y', (('type', 'z'), ('class', 'c')),
                  Counter('a'), Counter({'div': 1})),
                 ('close', 'div', (('class', 'a'),),
                  Counter(), Counter())]

        self.parser.feed(s)
        self.assertListEqual(self.parser.state, state)


class IssueParserTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = IssueParser()

    def _feed_file(self, file):
        file_path = os.path.join(dirname, file)
        with open(file_path, encoding='utf-8') as f:
            self.parser.feed(f.read())

    def _check_task(self):
        s = ('```\ndays_per_year = 365\n```\n'
             '```\nhours_per_day = 24\n```\n'
             '```\nminutes_per_hour = 60\n```\n'
             'Допишите программу так, чтобы она выводила '
             'количество минут в (не високосном) году, '
             'используя эти данные.Формат выводаВыводится '
             'одно число.')
        self.assertEqual(s, self.parser.task)

    def test_comments(self):
        self._feed_file('issue_comments.html')
        self._check_comments()

    def test_task(self):
        self._feed_file('issue_task.html')
        self._check_task()

    def test_full_page(self):
        self._feed_file('issue_page.html')
        self._check_task()
        self._check_comments()

        self.assertEqual('iPTiuyP6wvLCKlKJwNkR1WOKUtVJK8N1',
                         self.parser.token)