import requests
import re
from config import *


# first we have to get csrftoken:
def get_data():
    r = requests.get(DATA_URL, cookies={'sessionid': SESSION_ID})
    q = re.search("<table class=(.*?)</table>", r.content.decode().replace('\n','')).group(0)
    kids = [x.replace('&nbsp;', ' ') for x in re.findall('/">(.*?)</a>', q)]
    marks = [float(x) for x in re.findall('(\d*\.\d*)\s*</span>', q)]

    result = []
    for _ in range(0, len(kids)):
        result += [(kids[_], marks[_])]
    return result
