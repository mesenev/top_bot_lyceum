import requests
import re
import config


def login(username, passwd):
    s = requests.Session()
    r = s.get(config.LOGIN_URL)

    r = s.post(config.LOGIN_URL,
               data={'username': username,
                     'password': passwd,
                     'csrfmiddlewaretoken': s.cookies['sessionid']})

    return s.cookies['sessionid']