import requests

import config


def login(username, passwd):
    s = requests.Session()
    r = s.get(config.LOGIN_URL)

    r = s.post(config.LOGIN_URL,
               data={'username': username,
                     'password': passwd,
                     'csrfmiddlewaretoken': s.cookies['csrftoken']})
    if not r.url.startswith(config.LOGIN_URL):
        return s.cookies['sessionid'], s.cookies['csrftoken'], r.content.decode()
    else:
        return None, None
