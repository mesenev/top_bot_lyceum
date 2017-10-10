import unittest

from lyceum_api.issue import QueueTask


class JsonModelTestCase(unittest.TestCase):
    def test_queue_task_data(self):
        data = [{'DT_RowData': {'id': 60348},
                 'DT_RowId': 'row_issue_60348',
                 'has_issue_access': True,
                 'issue_url': '/issue/60348',
                 'mark': 7.0,
                 'responsible_name': 'Малявин  Никита',
                 'responsible_url': '/users/malyavin/',
                 'start': 0,
                 'status_color': '#F0AD4E',
                 'status_name': 'На проверке',
                 'student_name': 'Ефремов Александр',
                 'student_url': '/users/irinbrovkina/',
                 'task_title': 'Количество минут в году (*)',
                 'update_time': '08-10-2017 15:45'},
                {'DT_RowData': {'id': 60349},
                 'DT_RowId': 'row_issue_60349',
                 'has_issue_access': True,
                 'issue_url': '/issue/60349',
                 'mark': 0.0,
                 'responsible_name': 'Малявин  Никита',
                 'responsible_url': '/users/malyavin/',
                 'start': 0,
                 'status_color': '#F0AD4E',
                 'status_name': 'На проверке',
                 'student_name': 'Шаманский Виктор',
                 'student_url': '/users/viktor-21-ru/',
                 'task_title': 'Уравнение (*)',
                 'update_time': '08-10-2017 15:46'}]

        t1 = QueueTask(data[0])
        t2 = QueueTask(data[1])

        self.assertEqual(t1.student_name, 'Ефремов Александр')
        self.assertEqual(t1.id, 60348)
        self.assertEqual(t2.student_name, 'Шаманский Виктор')
        self.assertEqual(t2.id, 60349)
