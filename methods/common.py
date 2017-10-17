import re
import requests
from config import DATA_URL
from database import ActiveTop


def get_common_data_from_web(conf: ActiveTop, as_top=True):
    r = requests.get(conf.url, cookies={'sessionid': conf.token})
    try:
        q = re.search("<table class=(.*?)</table>", r.content.decode().replace('\n', '')).group(0)
    except AttributeError:
        return 1  # Login error
    kids = [x.replace('&nbsp;', ' ') for x in re.findall('/">(.*?)</a>', q)]
    marks = [float(x) for x in re.findall('(\d*\.\d*)\s*</span>', q)]

    result = []
    for _ in range(0, len(kids)):
        result += [(kids[_], marks[_])]
    return sorted(result, key=lambda t: t[1], reverse=True) if as_top else result
