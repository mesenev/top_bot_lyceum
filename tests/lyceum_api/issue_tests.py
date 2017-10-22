import asyncio
import os
import unittest
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest import mock

from lyceum_api.issue import get_issue, get_issue_async
from .parser_tests import IssueParserTestCase, dirname


class MockIssueRequestHandler(BaseHTTPRequestHandler):
    text = open(os.path.join(dirname,
                             'issue_page.html.test'),
                'rb').read()

    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(self.text)
        return


class IssueTestCase(unittest.TestCase):
    comments = IssueParserTestCase.comments
    task_text = IssueParserTestCase.task_text
    host = 'http://localhost:7357'

    @classmethod
    def setUpClass(cls):
        s = cls.mock_server = HTTPServer(('localhost', 7357),
                                         MockIssueRequestHandler)

        cls.mock_server_thread = Thread(target=s.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

    def _check_issue(self, task, comments, tok, mark):
        parser_comments = [vars(c) for c in comments]
        self.assertEqual(parser_comments, self.comments)
        self.assertEqual(task, self.task_text)
        self.assertEqual(mark, [7.1, 17])

    mock_config = mock.patch('config.HOME_LINK', new=host)
    mock_issue = mock.patch('lyceum_api.issue.HOME_LINK',
                            new=host, create=True)

    @mock_config
    @mock_issue
    def test_issue(self, *_):
        ret = get_issue('123', 60344)
        self._check_issue(*ret)

    @mock_config
    @mock_issue
    def test_issue_async(self, *_):
        tasks = []
        loop = asyncio.get_event_loop()
        for i in range(40):
            task = loop.run_in_executor(None,
                                        get_issue_async, '123', 60344)
            tasks.append(task)

        loop.run_until_complete(asyncio.gather(*tasks))