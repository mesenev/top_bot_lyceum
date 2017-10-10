import requests
import config


def login(username, passwd):
    s = requests.Session()
    r = s.get(config.LOGIN_URL)

    r = s.post(config.LOGIN_URL,
               data={'username': username,
                     'password': passwd,
                     'csrfmiddlewaretoken': s.cookies['csrftoken']})

    return s.cookies['sessionid']
