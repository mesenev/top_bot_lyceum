import requests
import re
from config import *


#first we have to get csrftoken:
r = requests.get(LOGIN_URL)

csrftoken = re.search("name='csrfmiddlewaretoken' value='(.*?)' />", r.content.decode('utf-8')).group(1)

# TODO: Make login work
r = requests.post(LOGIN_URL,
                  data={'username': LOGIN,
                        'password': PASSWORD,
                        'csrftoken': csrftoken}
                  )
login_cred = r.content.decode('utf-8')
SESSION_ID = login_cred