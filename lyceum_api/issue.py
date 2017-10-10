import requests


class QueueTask(object):
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


def get_check_queue(sid: str, n: int = 5):
    url = 'https://lms.yandexlyceum.ru/course/ajax_get_queue?' \
          'draw=2&start=0&length={}&lang=ru&timezone=Asia%2FVladivostok&' \
          'course_id=34&' \
          'filter=status_field%3D3'.format(n)

    data = requests.get(url, cookies={'sessionid': sid}).json()

    return data['data']
